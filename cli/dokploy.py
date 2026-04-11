#!/usr/bin/env python3
"""
Dokploy CLI - Official API Client
Based on Dokploy API documentation: https://docs.dokploy.com/docs/api

Authentication: x-api-key header (NOT Authorization: Bearer)
Base URL: https://your-dokploy-instance.com/api/
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any

VERSION = "1.0.1"

class DokployClient:
    """Official Dokploy API Client"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with correct x-api-key header"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            # Handle empty responses (common for deploy/restart/stop)
            if not response.text or response.text.strip() == '':
                return {'success': True, 'status': response.status_code}
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] API request failed: {e}")
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 401:
                    print("[ERROR] Invalid API key. Check your x-api-key header.")
                elif e.response.status_code == 404:
                    print(f"[ERROR] Endpoint not found: {endpoint}")
            raise
    
    # Projects
    def list_projects(self) -> Dict:
        """GET /api/project.all"""
        return self._request('GET', '/api/project.all')
    
    def create_project(self, name: str, description: str = "") -> Dict:
        """POST /api/project.create"""
        return self._request('POST', '/api/project.create', {
            'name': name,
            'description': description
        })
    
    # Applications
    def list_applications(self) -> list:
        """Get applications from project.all (application.all not available in all versions)"""
        projects = self.list_projects()
        apps = []
        for project in projects if isinstance(projects, list) else []:
            for env in project.get('environments', []):
                for app in env.get('applications', []):
                    apps.append({
                        'name': app.get('name'),
                        'id': app.get('applicationId'),
                        'status': app.get('applicationStatus'),
                        'project': project.get('name')
                    })
        return apps
    
    def create_application(self, name: str, environment_id: str, description: str = "") -> Dict:
        """POST /api/application.create"""
        return self._request('POST', '/api/application.create', {
            'name': name,
            'environmentId': environment_id,
            'description': description
        })
    
    def deploy_application(self, application_id: str, title: str = "", description: str = "") -> Dict:
        """POST /api/application.deploy"""
        return self._request('POST', '/api/application.deploy', {
            'applicationId': application_id,
            'title': title,
            'description': description
        })
    
    def restart_application(self, application_id: str) -> Dict:
        """POST /api/application.restart"""
        return self._request('POST', '/api/application.restart', {
            'applicationId': application_id
        })
    
    def stop_application(self, application_id: str) -> Dict:
        """POST /api/application.stop"""
        return self._request('POST', '/api/application.stop', {
            'applicationId': application_id
        })
    
    # Compose
    def list_compose(self) -> list:
        """Get compose from project.all (compose.all not available in all versions)"""
        projects = self.list_projects()
        compose_list = []
        for project in projects if isinstance(projects, list) else []:
            for env in project.get('environments', []):
                for compose in env.get('compose', []):
                    compose_list.append({
                        'name': compose.get('name', 'Unnamed'),
                        'id': compose.get('composeId'),
                        'project': project.get('name')
                    })
        return compose_list
    
    def deploy_compose(self, compose_id: str) -> Dict:
        """POST /api/compose.deploy"""
        return self._request('POST', '/api/compose.deploy', {
            'composeId': compose_id
        })
    
    # User
    def get_user(self) -> Dict:
        """GET /api/user.get"""
        return self._request('GET', '/api/user.get')
    
    def create_api_key(self, name: str, organization_id: str, **kwargs) -> Dict:
        """POST /api/user.createApiKey"""
        data = {
            'name': name,
            'metadata': {
                'organizationId': organization_id
            }
        }
        data.update(kwargs)
        return self._request('POST', '/api/user.createApiKey', data)


def load_config() -> tuple:
    """Load configuration from environment or files"""
    # Try environment variables first
    base_url = os.environ.get('DOKPLOY_URL')
    api_key = os.environ.get('DOKPLOY_API_KEY') or os.environ.get('DOKPLOY_TOKEN')
    
    # Try loading from secrets/dokploy.env
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
        description='Dokploy CLI - Official API Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DOKPLOY_URL       Your Dokploy instance URL
  DOKPLOY_API_KEY   Your API key (x-api-key header)

Examples:
  dokploy projects list
  dokploy apps list
  dokploy apps deploy --id APP_ID
  dokploy compose list
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('--url', help='Dokploy URL (overrides env)')
    parser.add_argument('--key', help='API key (overrides env)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Projects
    project_parser = subparsers.add_parser('projects', help='Project operations')
    project_sub = project_parser.add_subparsers(dest='project_cmd')
    project_sub.add_parser('list', help='List all projects')
    create_proj = project_sub.add_parser('create', help='Create new project')
    create_proj.add_argument('name')
    create_proj.add_argument('--description', default='')
    
    # Applications
    app_parser = subparsers.add_parser('apps', help='Application operations')
    app_sub = app_parser.add_subparsers(dest='app_cmd')
    app_sub.add_parser('list', help='List all applications')
    deploy_app = app_sub.add_parser('deploy', help='Deploy application')
    deploy_app.add_argument('--id', required=True, help='Application ID')
    deploy_app.add_argument('--title', default='')
    restart_app = app_sub.add_parser('restart', help='Restart application')
    restart_app.add_argument('--id', required=True)
    stop_app = app_sub.add_parser('stop', help='Stop application')
    stop_app.add_argument('--id', required=True)
    
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
    
    # Override with CLI args
    if args.url:
        base_url = args.url
    if args.key:
        api_key = args.key
    
    if not base_url or not api_key:
        print("[ERROR] Missing DOKPLOY_URL or DOKPLOY_API_KEY")
        print("Set environment variables or use --url and --key")
        sys.exit(1)
    
    # Create client
    client = DokployClient(base_url, api_key)
    
    try:
        # Execute command
        if args.command == 'projects':
            if args.project_cmd == 'list':
                result = client.list_projects()
                data = result if isinstance(result, list) else result.get('result', {}).get('data', {}).get('json', [])
                print(f"Projects found: {len(data)}")
                for proj in data:
                    print(f"  - {proj.get('name')} ({proj.get('id')})")
                    
            elif args.project_cmd == 'create':
                result = client.create_project(args.name, args.description)
                print(f"Created project: {result}")
        
        elif args.command == 'apps':
            if args.app_cmd == 'list':
                apps = client.list_applications()
                print(f"Applications found: {len(apps)}")
                print()
                for app in apps:
                    print(f"  - {app.get('name')}")
                    print(f"    ID: {app.get('id')}")
                    print(f"    Status: {app.get('status')}")
                    print(f"    Project: {app.get('project')}")
                    print()
                    
            elif args.app_cmd == 'deploy':
                result = client.deploy_application(args.id, args.title)
                print(f"Deploy initiated: {result}")
                
            elif args.app_cmd == 'restart':
                result = client.restart_application(args.id)
                print(f"Restart initiated: {result}")
                
            elif args.app_cmd == 'stop':
                result = client.stop_application(args.id)
                print(f"Stop initiated: {result}")
        
        elif args.command == 'compose':
            if args.compose_cmd == 'list':
                compose_list = client.list_compose()
                print(f"Compose projects found: {len(compose_list)}")
                print()
                for comp in compose_list:
                    print(f"  - {comp.get('name')}")
                    print(f"    ID: {comp.get('id')}")
                    print(f"    Project: {comp.get('project')}")
                    print()
                    
            elif args.compose_cmd == 'deploy':
                result = client.deploy_compose(args.id)
                print(f"Deploy initiated: {result}")
        
        elif args.command == 'user':
            if args.user_cmd == 'info':
                result = client.get_user()
                print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
