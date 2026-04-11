#!/usr/bin/env python3
"""
Dokploy CLI - Universal API Client
Supports both REST and tRPC API formats
Auto-detects API version
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

VERSION = "2.0.0"

class DokployClient:
    """Universal Dokploy API Client - REST and tRPC"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/').replace('/api', '')
        self.api_key = api_key
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
        }
        self.is_trpc = False
        self._detect_api_type()
    
    def _detect_api_type(self):
        """Auto-detect if server uses REST or tRPC"""
        # Try REST first (more common in older versions)
        try:
            url = f"{self.base_url}/api/project.all"
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                self.is_trpc = False
                print("[INFO] Using REST API")
                return
        except:
            pass
        
        # Try tRPC
        try:
            url = f"{self.base_url}/api/trpc/project.all?batch=1"
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                self.is_trpc = True
                print("[INFO] Using tRPC API")
                return
        except:
            pass
        
        # Default to REST
        self.is_trpc = False
        print("[INFO] Defaulting to REST API")
    
    def _request(self, procedure: str, payload: Optional[Dict] = None, method: str = 'POST') -> Any:
        """Make API request (auto-detects format)"""
        if self.is_trpc:
            return self._trpc_request(procedure, payload, method)
        else:
            return self._rest_request(procedure, payload, method)
    
    def _trpc_request(self, procedure: str, payload: Optional[Dict], method: str) -> Any:
        """Make tRPC request with batching"""
        url = f"{self.base_url}/api/trpc/{procedure}?batch=1"
        data = {"0": payload} if payload else None
        
        if method == 'GET':
            resp = requests.get(url, headers=self.headers, timeout=30)
        else:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)
        
        resp.raise_for_status()
        
        if not resp.text:
            return {'success': True}
        
        result = resp.json()
        # Extract from batch format
        if isinstance(result, list) and len(result) > 0:
            item = result[0]
            if 'result' in item and 'data' in item['result']:
                return item['result']['data'].get('json', item['result']['data'])
            return item.get('result', item)
        return result
    
    def _rest_request(self, endpoint: str, payload: Optional[Dict], method: str) -> Any:
        """Make REST request"""
        url = f"{self.base_url}/api/{endpoint}"
        
        if method == 'GET':
            resp = requests.get(url, headers=self.headers, timeout=30)
        else:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
        
        resp.raise_for_status()
        
        if not resp.text:
            return {'success': True}
        
        return resp.json()
    
    def _extract_array(self, data: Any) -> List:
        """Extract array from various response formats"""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Try common response patterns
            if 'result' in data:
                return self._extract_array(data['result'])
            if 'data' in data:
                return self._extract_array(data['data'])
            if 'json' in data:
                return data['json']
        return []
    
    # Projects
    def list_projects(self) -> List:
        """List all projects"""
        if self.is_trpc:
            return self._trpc_request('project.all', None, 'GET')
        else:
            data = self._rest_request('project.all', None, 'GET')
            return data if isinstance(data, list) else []
    
    # Applications
    def list_applications(self) -> List:
        """List all applications"""
        if self.is_trpc:
            return self._trpc_request('application.all', None, 'GET')
        else:
            # REST: extract from project.all
            projects = self.list_projects()
            apps = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for app in env.get('applications', []):
                        apps.append(app)
            return apps
    
    def deploy_application(self, app_id: str, title: str = "") -> Dict:
        """Deploy application"""
        payload = {'applicationId': app_id, 'title': title}
        if self.is_trpc:
            return self._trpc_request('application.deploy', payload, 'POST')
        else:
            return self._rest_request('application.deploy', payload, 'POST')
    
    def reload_application(self, app_id: str) -> Dict:
        """Restart application (uses reload in tRPC)"""
        payload = {'applicationId': app_id}
        if self.is_trpc:
            return self._trpc_request('application.reload', payload, 'POST')
        else:
            # Try reload, then restart
            try:
                return self._rest_request('application.reload', payload, 'POST')
            except:
                return self._rest_request('application.restart', payload, 'POST')
    
    def stop_application(self, app_id: str) -> Dict:
        """Stop application"""
        payload = {'applicationId': app_id}
        if self.is_trpc:
            return self._trpc_request('application.stop', payload, 'POST')
        else:
            return self._rest_request('application.stop', payload, 'POST')
    
    def start_application(self, app_id: str) -> Dict:
        """Start application"""
        payload = {'applicationId': app_id}
        if self.is_trpc:
            return self._trpc_request('application.start', payload, 'POST')
        else:
            return self._rest_request('application.start', payload, 'POST')
    
    def remove_application(self, app_id: str) -> Dict:
        """Remove application"""
        payload = {'applicationId': app_id}
        if self.is_trpc:
            return self._trpc_request('application.remove', payload, 'POST')
        else:
            return self._rest_request('application.remove', payload, 'POST')
    
    # Compose
    def list_compose(self) -> List:
        """List all compose projects"""
        if self.is_trpc:
            return self._trpc_request('compose.all', None, 'GET')
        else:
            # Extract from project.all
            projects = self.list_projects()
            compose_list = []
            for proj in projects:
                for env in proj.get('environments', []):
                    for comp in env.get('compose', []):
                        compose_list.append(comp)
            return compose_list
    
    def deploy_compose(self, compose_id: str) -> Dict:
        """Deploy compose"""
        payload = {'composeId': compose_id}
        if self.is_trpc:
            return self._trpc_request('compose.deploy', payload, 'POST')
        else:
            return self._rest_request('compose.deploy', payload, 'POST')
    
    # User
    def get_user(self) -> Dict:
        """Get user info"""
        if self.is_trpc:
            return self._trpc_request('user.get', None, 'GET')
        else:
            return self._rest_request('user.get', None, 'GET')


def load_config() -> tuple:
    """Load configuration"""
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
        description='Dokploy CLI - Universal API Client (REST & tRPC)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DOKPLOY_URL       Your Dokploy instance URL
  DOKPLOY_API_KEY   Your API key

The CLI auto-detects REST or tRPC API format.

Examples:
  dokploy projects list
  dokploy apps list
  dokploy apps deploy --id APP_ID
  dokploy apps restart --id APP_ID
        """
    )
    
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Projects
    project_parser = subparsers.add_parser('projects', help='Project operations')
    project_sub = project_parser.add_subparsers(dest='project_cmd')
    project_sub.add_parser('list', help='List all projects')
    
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
    start_app = app_sub.add_parser('start', help='Start application')
    start_app.add_argument('--id', required=True)
    remove_app = app_sub.add_parser('remove', help='Remove application')
    remove_app.add_argument('--id', required=True)
    
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
        sys.exit(1)
    
    # Create client
    client = DokployClient(base_url, api_key)
    
    try:
        if args.command == 'projects':
            if args.project_cmd == 'list':
                projects = client.list_projects()
                print(f"Projects found: {len(projects)}")
                for proj in projects:
                    print(f"  - {proj.get('name')} ({proj.get('projectId', 'N/A')})")
        
        elif args.command == 'apps':
            if args.app_cmd == 'list':
                apps = client.list_applications()
                print(f"Applications found: {len(apps)}")
                for app in apps:
                    print(f"  - {app.get('name')} ({app.get('applicationId', 'N/A')}) - {app.get('applicationStatus', 'unknown')}")
                    
            elif args.app_cmd == 'deploy':
                result = client.deploy_application(args.id, args.title)
                print("Deploy initiated successfully")
                
            elif args.app_cmd == 'restart':
                result = client.reload_application(args.id)
                print("Restart initiated successfully")
                
            elif args.app_cmd == 'stop':
                result = client.stop_application(args.id)
                print("Stop initiated successfully")
                
            elif args.app_cmd == 'start':
                result = client.start_application(args.id)
                print("Start initiated successfully")
                
            elif args.app_cmd == 'remove':
                result = client.remove_application(args.id)
                print("Remove initiated successfully")
        
        elif args.command == 'compose':
            if args.compose_cmd == 'list':
                compose_list = client.list_compose()
                print(f"Compose projects found: {len(compose_list)}")
                for comp in compose_list:
                    print(f"  - {comp.get('name')} ({comp.get('composeId', 'N/A')})")
                    
            elif args.compose_cmd == 'deploy':
                result = client.deploy_compose(args.id)
                print("Deploy initiated successfully")
        
        elif args.command == 'user':
            if args.user_cmd == 'info':
                user = client.get_user()
                print(json.dumps(user, indent=2))
    
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
