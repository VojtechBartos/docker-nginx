# -*- coding: utf-8 -*-
# http://google-styleguide.googlecode.com/svn/trunk/pyguide.html

import os
import shutil
from urlparse import urlparse


def detect_linked_containers(environ):
    """
    Detect linked containers which wanna use nginx config
    :param environ: {dict} environment variables
    :return: {dict} of detected containers
    """
    containers = {}

    for name, value in environ.iteritems():
        parts = name.split('_')
        config = {}

        if name.endswith('_PORT') and len(parts) == 2:
            config.update({
                'port': urlparse(value).port
            })
        elif name.endswith('_ENV_HOSTNAME') and len(parts) == 4:
            config.update({
                'hostname': value
            })
        elif name.endswith('_ENV_NGINX_TEMPLATE') and len(parts) == 4:
            config.update({
                'template': value
            })

        if len(config.keys()) > 0:
            container = containers.get(parts[0], {})
            container.update(config)
            containers[parts[0]] = container

    return containers


def generate_sites_for_containers(containers, default_config="basic_proxy.conf"):
    """
    Generating sites configs for containers and saving them to appropriate path
    :param containers: {dict} of detected containers
    :param default_config: {str} default config file name
    """
    for name, settings in containers.iteritems():
        template = settings.get('template', default_config)
        port = settings.get('port', 8000)
        hostname = settings.get('hostname')

        assert isinstance(hostname, (str, unicode))

        template_path = '/etc/nginx/templates/{0}'.format(template)
        conf_path = '/etc/nginx/sites-enabled/container_{0}.conf'.format(name)

        # creating template
        with open(template_path, 'r') as f:
            template = f.read() \
                        .replace("{{hostname}}", hostname) \
                        .replace("{{container_name}}", name) \
                        .replace("{{container_port}}", str(port))

        # saving template
        with open(conf_path, 'w+') as f:
            f.write(template)


if __name__ == "__main__":
    # detect all containers which wanna use nginx
    containers = detect_linked_containers(os.environ)

    # generate sites configs for those containers
    generate_sites_for_containers(containers)
