import json
import subprocess


def docker_names():
    """Get docker names"""
    command = 'docker ps --format "{{.Names}}"'
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    names = process.stdout.readlines()
    if names:
        names = [s.decode('ascii').replace('\n', '') for s in names]
        mysql = [k for k in names if '_mysql_' in k][0]
        wikibase = [k for k in names if '_wikibase_' in k][0]
        output = [mysql, wikibase]
    else:
        output = None
    process.poll()
    return output


def docker_inspect(container):
    """Wrapper for 'docker inspect'. Returns dictionary of settings or empty
    dictionary in case of error."""
    result = subprocess.run(
        ['docker', 'inspect', container],
        capture_output=True,
    )
    if result.returncode != 0:
        print("Error querying docker daemon:", result.stdout, result.stderr)
        return {}
    return json.loads(result.stdout)[0]


def docker_env(container):
    """Returns dictionary of container environment variables or empty
    dictionary in case of error."""
    settings = docker_inspect(container)
    if not len(settings):
        return {}
    env_list = settings["Config"]["Env"]
    return {i[0:i.find('=')]: i[i.find('=') + 1:] for i in env_list}


def docker_ports(container):
    """Returns dictionary of container network ports or empty dictionary in
    case of error."""
    settings = docker_inspect(container)
    if not len(settings):
        return {}
    port_dict = settings["NetworkSettings"]["Ports"]
    return port_dict
