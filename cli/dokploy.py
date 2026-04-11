#!/usr/bin/env python3
"""
Dokploy CLI - REST API Client for VetGroom Tower
Based on official Dokploy REST API: https://docs.dokploy.com/docs/api

Authentication: x-api-key header
Base URL: https://instance.com/api/
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

VERSION = "2.1.0"

class DokployClient:
    """Dokploy REST API Client"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/').replace('/api', '')
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make REST API request"""
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
            print(f"[ERROR] {e}")
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    print("[ERROR] Invalid API key")
                elif e.response.status_code == 404:
                    print(f"[ERROR] Endpoint not found: {endpoint}")
            raise
    
    # Projects
    def list_projects(self) -> List:
        """GET /api/project.all"""
        return self._request('GET', 'project.all')
    
    def get_project(self, project_id: str) -> Dict:
        """GET /api/project.one?projectId=xxx"""
        # Note: Some versions use query params, others use body
        return self._request('GET', f'project.one?projectId={project_id}')
    
    # Applications
    def list_applications(self) -> List:
        """GET /api/application.all"""
        try:
            return self._request('GET', 'application.all')
        except:
            # Fallback: extract from projects
            projects = self.list_projects()
            apps = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for app in env.get('applications', []):
                        apps.append(app)
            return apps
    
    def get_application(self, app_id: str) -> Dict:
        """GET /api/application.one?applicationId=xxx"""
        return self._request('GET', f'application.one?applicationId={app_id}')
    
    def deploy_application(self, app_id: str, title: str = "") -> Dict:
        """POST /api/application.deploy"""
        return self._request('POST', 'application.deploy', {
            'applicationId': app_id,
            'title': title
        })
    
    def rebuild_application(self, app_id: str) -> Dict:
        """POST /api/application.rebuild"""
        return self._request('POST', 'application.rebuild', {
            'applicationId': app_id
        })
    
    def stop_application(self, app_id: str) -> Dict:
        """POST /api/application.stop"""
        return self._request('POST', 'application.stop', {
            'applicationId': app_id
        })
    
    def start_application(self, app_id: str) -> Dict:
        """POST /api/application.start"""
        return self._request('POST', 'application.start', {
            'applicationId': app_id
        })
    
    # Deployments
    def list_deployments(self, app_id: Optional[str] = None) -> List:
        """GET /api/deployment.all or /api/deployment.all?applicationId=xxx"""
        endpoint = 'deployment.all'
        if app_id:
            endpoint += f'?applicationId={app_id}'
        return self._request('GET', endpoint)
    
    def get_deployment_logs(self, deployment_id: str) -> str:
        """GET /api/deployment.getLogs?deploymentId=xxx"""
        return self._request('GET', f'deployment.getLogs?deploymentId={deployment_id}')
    
    # Compose
    def list_compose(self) -> List:
        """GET /api/compose.all"""
        try:
            return self._request('GET', 'compose.all')
        except:
            # Fallback: extract from projects
            projects = self.list_projects()
            compose_list = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for comp in env.get('compose', []):
                        compose_list.append(comp)
            return compose_list
    
    def deploy_compose(self, compose_id: str) -> Dict:
        """POST /api/compose.deploy"""
        return self._request('POST', 'compose.deploy', {
            'composeId': compose_id
        })
    
    # User
    def get_user(self) -> Dict:
        """GET /api/user.get"""
        return self._request('GET', 'user.get')
    
    def create_api_key(self, name: str, **kwargs) -> Dict:
        """POST /api/user.createApiKey"""
        payload = {'name': name, **kwargs}
        return self._request('POST', 'user.createApiKey', payload)


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
        description='Dokploy CLI - REST API Client for VetGroom Tower',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DOKPLOY_URL       Your Dokploy instance URL
  DOKPLOY_API_KEY   Your API key (x-api-key header)

Examples:
  dokploy projects list
  dokploy apps list
  dokploy apps deploy --id APP_ID
  dokploy deployments list --app APP_ID
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
    deploy_app = app_sub.add_parser('deploy', help='Deploy application')
    deploy_app.add_argument('--id', required=True, help='Application ID')
    deploy_app.add_argument('--title', default='', help='Deployment title')
    rebuild_app = app_sub.add_parser('rebuild', help='Rebuild application')
    rebuild_app.add_argument('--id', required=True, help='Application ID')
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
    
    # User
    user_parser = subparsers.add_parser('user', help='User operations')
    user_sub = user_parser.add_subparsers(dest='user_cmd')
    user_sub.add_parser('info', help='Get user info')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load config
    base_url, api_key = load_config()
    
    if not base_url or not api_key:
        print("[ERROR] Missing DOKPLOY_URL or DOKPLOY_API_KEY")
        print("Set environment variables or create secrets/dokploy.env")
        sys.exit(1)
    
    # Create client
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
            
            elif args.app_cmd == 'rebuild':
                result = client.rebuild_application(args.id)
                print("[OK] Rebuild initiated successfully")
            
            elif args.app_cmd == 'stop':
                result = client.stop_application(args.id)
                print("[OK] Stop initiated successfully")
            
            elif args.app_cmd == 'start':
                result = client.start_application(args.id)
                print("[OK] Start initiated successfully")
        
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
        
        elif args.command == 'user':
            if args.user_cmd == 'info':
                user = client.get_user()
                print(json.dumps(user, indent=2))
    
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
