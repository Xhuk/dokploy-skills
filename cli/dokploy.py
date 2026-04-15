#!/usr/bin/env python3
"""
Dokploy CLI - Hybrid REST + tRPC API Client
Based on official Dokploy API: https://docs.dokploy.com/docs/api

Dokploy API support is not always uniform across installs. Some servers expose:
  - OpenAPI/REST:  GET/POST /api/<procedure>
  - tRPC:          POST /api/trpc/<procedure> with {"json": payload}

Important:
  - Do not assume one API layer works for every endpoint.
  - Prefer endpoint-level fallback instead of version-wide assumptions.

Authentication: x-api-key header
Base URL: https://instance.com/
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

VERSION = "2.2.0"


class DokployClient:
    """Dokploy Hybrid API Client (REST + tRPC)"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/').replace('/api', '').replace('/trpc', '')
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
        }

    def _rest_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Call OpenAPI/REST endpoint: /api/<procedure>"""
        url = f"{self.base_url}/api/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=self.headers, timeout=30)
            else:
                resp = requests.post(url, headers=self.headers, json=data, timeout=30)
            resp.raise_for_status()
            if not resp.text:
                return {'success': True, 'status': resp.status_code}
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR REST] {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    print("[ERROR] Invalid API key")
                elif e.response.status_code == 404:
                    print(f"[ERROR] Endpoint not found: {endpoint}")
            raise

    def _trpc_request(self, procedure: str, payload: Optional[Dict] = None) -> Any:
        """Call tRPC mutation endpoint: POST /api/trpc/<procedure> with {json: payload}"""
        url = f"{self.base_url}/api/trpc/{procedure}"
        body = {"json": payload} if payload is not None else {}
        try:
            resp = requests.post(url, headers=self.headers, json=body, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            # tRPC wraps successful results in result.data.json
            if isinstance(result, dict) and "result" in result:
                inner = result["result"]
                if isinstance(inner, dict) and "data" in inner:
                    return inner["data"].get("json", inner["data"])
            return result
        except requests.exceptions.RequestException as e:
            print(f"[ERROR tRPC] {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    print("[ERROR] Invalid API key")
                elif e.response.status_code == 404:
                    print(f"[ERROR] tRPC procedure not found: {procedure}")
                else:
                    print(f"[ERROR] Response: {e.response.text[:500]}")
            raise

    def _extract_app_from_projects(self, app_id: str) -> Dict:
        """Fallback when application.one/application.all is unavailable on a server."""
        projects = self.list_projects()
        for proj in projects:
            for env in proj.get('environments', []):
                for app in env.get('applications', []):
                    if app.get('applicationId') == app_id:
                        return app
        raise KeyError(f"Application not found via project.all fallback: {app_id}")

    # Projects
    def list_projects(self) -> List:
        """GET /api/project.all"""
        return self._rest_request('GET', 'project.all')

    def get_project(self, project_id: str) -> Dict:
        """GET /api/project.one?projectId=xxx"""
        return self._rest_request('GET', f'project.one?projectId={project_id}')

    # Applications
    def list_applications(self) -> List:
        """GET /api/application.all"""
        try:
            return self._rest_request('GET', 'application.all')
        except Exception:
            projects = self.list_projects()
            apps = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for app in env.get('applications', []):
                        apps.append(app)
            return apps

    def get_application(self, app_id: str) -> Dict:
        """GET /api/application.one?applicationId=xxx"""
        try:
            return self._rest_request('GET', f'application.one?applicationId={app_id}')
        except Exception:
            return self._extract_app_from_projects(app_id)

    def update_application(self, app_id: str, **fields) -> Dict:
        """POST /api/application.update (REST) or /api/trpc/application.update (tRPC fallback)"""
        payload = {"applicationId": app_id, **fields}
        try:
            return self._rest_request('POST', 'application.update', payload)
        except requests.exceptions.HTTPError as e:
            # If REST returns 500/Invalid JSON, fallback to tRPC
            if e.response is not None and e.response.status_code in (400, 500):
                return self._trpc_request('application.update', payload)
            raise

    def deploy_application(self, app_id: str, title: str = "") -> Any:
        """Deploy app, preferring REST and falling back to tRPC when needed."""
        payload = {
            'applicationId': app_id,
            'title': title
        }
        try:
            return self._rest_request('POST', 'application.deploy', payload)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (400, 404, 405, 500):
                return self._trpc_request('application.deploy', payload)
            raise

    def rebuild_application(self, app_id: str) -> Any:
        """Rebuild app, preferring REST and falling back to tRPC when needed."""
        payload = {'applicationId': app_id}
        try:
            return self._rest_request('POST', 'application.rebuild', payload)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (400, 404, 405, 500):
                return self._trpc_request('application.rebuild', payload)
            raise

    def stop_application(self, app_id: str) -> Any:
        """POST /api/application.stop"""
        return self._rest_request('POST', 'application.stop', {
            'applicationId': app_id
        })

    def start_application(self, app_id: str) -> Any:
        """POST /api/application.start"""
        return self._rest_request('POST', 'application.start', {
            'applicationId': app_id
        })

    def restart_application(self, app_id: str) -> Any:
        """POST /api/application.restart"""
        payload = {'applicationId': app_id}
        try:
            return self._rest_request('POST', 'application.restart', payload)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                self.stop_application(app_id)
                return self.start_application(app_id)
            raise

    # Deployments
    def list_deployments(self, app_id: str) -> List:
        """GET /api/deployment.all?applicationId=xxx"""
        return self._rest_request('GET', f'deployment.all?applicationId={app_id}')

    def get_deployment_logs(self, deployment_id: str) -> str:
        """GET /api/deployment.getLogs?deploymentId=xxx"""
        return self._rest_request('GET', f'deployment.getLogs?deploymentId={deployment_id}')

    # Compose
    def list_compose(self) -> List:
        """GET /api/compose.all"""
        try:
            return self._rest_request('GET', 'compose.all')
        except Exception:
            projects = self.list_projects()
            compose_list = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for comp in env.get('compose', []):
                        compose_list.append(comp)
            return compose_list

    def deploy_compose(self, compose_id: str) -> Any:
        """POST /api/compose.deploy"""
        return self._rest_request('POST', 'compose.deploy', {
            'composeId': compose_id
        })

    # Docker containers (read-only)
    def list_containers(self) -> List:
        """GET /api/trpc/docker.getContainers?input={json:{}}"""
        url = f"{self.base_url}/api/trpc/docker.getContainers?input=%7B%22json%22%3A%7B%7D%7D"
        resp = requests.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, dict) and "result" in result:
            inner = result["result"]
            if isinstance(inner, dict) and "data" in inner:
                return inner["data"].get("json", [])
        return result

    # User
    def get_user(self) -> Dict:
        """GET /api/user.get"""
        return self._rest_request('GET', 'user.get')

    def create_api_key(self, name: str, **kwargs) -> Dict:
        """POST /api/user.createApiKey"""
        payload = {'name': name, **kwargs}
        return self._rest_request('POST', 'user.createApiKey', payload)


def load_config() -> tuple:
    """Load configuration from environment or files"""
    base_url = os.environ.get('DOKPLOY_URL')
    api_key = os.environ.get('DOKPLOY_API_KEY') or os.environ.get('DOKPLOY_TOKEN')

    if not base_url or not api_key:
        env_file = Path('secrets/dokploy.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == 'DOKPLOY_URL' and not base_url:
                            base_url = value
                        elif key in ('DOKPLOY_API_KEY', 'DOKPLOY_TOKEN') and not api_key:
                            api_key = value

    return base_url, api_key


def main():
    parser = argparse.ArgumentParser(
        description='Dokploy CLI - Hybrid REST + tRPC API Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DOKPLOY_URL       Your Dokploy instance URL (e.g. http://dokploy.example.com)
  DOKPLOY_API_KEY   Your API key (x-api-key header)

Examples:
  dokploy projects list
  dokploy apps list
  dokploy apps get --id APP_ID
  dokploy apps deploy --id APP_ID --title "Hotfix login"
  dokploy apps update --id APP_ID --repository my-repo --branch main --dockerfile Dockerfile
  dokploy apps restart --id APP_ID
  dokploy deployments list --app APP_ID
  dokploy containers list
        """
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Projects
    project_parser = subparsers.add_parser('projects', help='Project operations')
    project_sub = project_parser.add_subparsers(dest='project_cmd')
    project_sub.add_parser('list', help='List all projects')
    get_proj = project_sub.add_parser('get', help='Get project details')
    get_proj.add_argument('--id', required=True, help='Project ID')

    # Applications
    app_parser = subparsers.add_parser('apps', help='Application operations')
    app_sub = app_parser.add_subparsers(dest='app_cmd')
    app_sub.add_parser('list', help='List all applications')
    get_app = app_sub.add_parser('get', help='Get application details')
    get_app.add_argument('--id', required=True, help='Application ID')

    deploy_app = app_sub.add_parser('deploy', help='Deploy application (REST first, tRPC fallback)')
    deploy_app.add_argument('--id', required=True, help='Application ID')
    deploy_app.add_argument('--title', default='', help='Deployment title')

    update_app = app_sub.add_parser('update', help='Update application source/config')
    update_app.add_argument('--id', required=True, help='Application ID')
    update_app.add_argument('--repository', default=None, help='Git repository name')
    update_app.add_argument('--branch', default=None, help='Git branch')
    update_app.add_argument('--dockerfile', default=None, help='Dockerfile path')
    update_app.add_argument('--build-path', default=None, help='Build context path')
    update_app.add_argument('--auto-deploy', choices=['true', 'false'], default=None, help='Enable/disable auto deploy')

    rebuild_app = app_sub.add_parser('rebuild', help='Rebuild application')
    rebuild_app.add_argument('--id', required=True, help='Application ID')

    restart_app = app_sub.add_parser('restart', help='Restart application')
    restart_app.add_argument('--id', required=True)

    stop_app = app_sub.add_parser('stop', help='Stop application')
    stop_app.add_argument('--id', required=True)

    start_app = app_sub.add_parser('start', help='Start application')
    start_app.add_argument('--id', required=True)

    # Deployments
    deploy_parser = subparsers.add_parser('deployments', help='Deployment operations')
    deploy_sub = deploy_parser.add_subparsers(dest='deploy_cmd')
    list_deploy = deploy_sub.add_parser('list', help='List deployments')
    list_deploy.add_argument('--app', help='Filter by application ID')
    logs_deploy = deploy_sub.add_parser('logs', help='Get deployment logs')
    logs_deploy.add_argument('--id', required=True, help='Deployment ID')

    # Compose
    compose_parser = subparsers.add_parser('compose', help='Docker Compose operations')
    compose_sub = compose_parser.add_subparsers(dest='compose_cmd')
    compose_sub.add_parser('list', help='List all compose projects')
    deploy_compose = compose_sub.add_parser('deploy', help='Deploy compose')
    deploy_compose.add_argument('--id', required=True, help='Compose ID')

    # Containers
    container_parser = subparsers.add_parser('containers', help='Docker container operations')
    container_sub = container_parser.add_subparsers(dest='container_cmd')
    container_sub.add_parser('list', help='List running containers')

    # User
    user_parser = subparsers.add_parser('user', help='User operations')
    user_sub = user_parser.add_subparsers(dest='user_cmd')
    user_sub.add_parser('info', help='Get user info')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    base_url, api_key = load_config()

    if not base_url or not api_key:
        print("[ERROR] Missing DOKPLOY_URL or DOKPLOY_API_KEY")
        print("Set environment variables or create secrets/dokploy.env")
        sys.exit(1)

    client = DokployClient(base_url, api_key)

    try:
        if args.command == 'projects':
            if args.project_cmd == 'list':
                projects = client.list_projects()
                print(f"Projects found: {len(projects)}\n")
                for proj in projects:
                    print(f"  - {proj.get('name')}")
                    print(f"    ID: {proj.get('projectId')}")
                    desc = proj.get('description', '')
                    if desc:
                        print(f"    Description: {desc}")
                    print()

            elif args.project_cmd == 'get':
                proj = client.get_project(args.id)
                print(json.dumps(proj, indent=2))

        elif args.command == 'apps':
            if args.app_cmd == 'list':
                apps = client.list_applications()
                print(f"Applications found: {len(apps)}\n")
                for app in apps:
                    app_id = app.get('applicationId', app.get('id', 'N/A'))
                    print(f"  - {app.get('name')}")
                    print(f"    ID: {app_id}")
                    print(f"    Status: {app.get('applicationStatus', 'unknown')}")
                    print()

            elif args.app_cmd == 'get':
                app = client.get_application(args.id)
                print(json.dumps(app, indent=2))

            elif args.app_cmd == 'deploy':
                result = client.deploy_application(args.id, args.title)
                print("[OK] Deploy initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

            elif args.app_cmd == 'update':
                fields = {}
                if args.repository is not None:
                    fields['repository'] = args.repository
                if args.branch is not None:
                    fields['branch'] = args.branch
                if args.dockerfile is not None:
                    fields['dockerfile'] = args.dockerfile
                if args.build_path is not None:
                    fields['buildPath'] = args.build_path
                if args.auto_deploy is not None:
                    fields['autoDeploy'] = args.auto_deploy == 'true'

                if not fields:
                    print("[ERROR] No update fields provided. Use --repository, --branch, --dockerfile, --build-path, or --auto-deploy")
                    sys.exit(1)

                result = client.update_application(args.id, **fields)
                print("[OK] Application updated successfully")
                print(json.dumps(result, indent=2))

            elif args.app_cmd == 'rebuild':
                result = client.rebuild_application(args.id)
                print("[OK] Rebuild initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

            elif args.app_cmd == 'restart':
                result = client.restart_application(args.id)
                print("[OK] Restart initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

            elif args.app_cmd == 'stop':
                result = client.stop_application(args.id)
                print("[OK] Stop initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

            elif args.app_cmd == 'start':
                result = client.start_application(args.id)
                print("[OK] Start initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

        elif args.command == 'deployments':
            if args.deploy_cmd == 'list':
                deployments = client.list_deployments(args.app)
                print(f"Deployments found: {len(deployments)}\n")
                for dep in deployments:
                    print(f"  - {dep.get('title', 'Untitled')}")
                    print(f"    ID: {dep.get('deploymentId')}")
                    print(f"    Status: {dep.get('status')}")
                    print()

            elif args.deploy_cmd == 'logs':
                logs = client.get_deployment_logs(args.id)
                print(logs)

        elif args.command == 'compose':
            if args.compose_cmd == 'list':
                compose_list = client.list_compose()
                print(f"Compose projects found: {len(compose_list)}\n")
                for comp in compose_list:
                    print(f"  - {comp.get('name')}")
                    print(f"    ID: {comp.get('composeId', comp.get('id', 'N/A'))}")
                    print()

            elif args.compose_cmd == 'deploy':
                result = client.deploy_compose(args.id)
                print("[OK] Deploy initiated successfully")
                if result:
                    print(json.dumps(result, indent=2))

        elif args.command == 'containers':
            if args.container_cmd == 'list':
                containers = client.list_containers()
                print(f"Containers found: {len(containers)}\n")
                for c in containers:
                    print(f"  - {c.get('name')} ({c.get('image')})")
                    print(f"    State: {c.get('state')} | Status: {c.get('status')}")
                    print()

        elif args.command == 'user':
            if args.user_cmd == 'info':
                user = client.get_user()
                print(json.dumps(user, indent=2))

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
