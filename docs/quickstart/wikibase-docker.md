---
layout: default
title: Wikibase Docker
parent: QuickStart
nav_order: 2a
---
# Wikibase Docker

RaiseWikibase is based on [Wikibase Docker](https://github.com/wmde/wikibase-release-pipeline) developed by [Wikimedia Germany](https://wikimedia.de). [Wikibase Docker](https://github.com/wmde/wikibase-release-pipeline) is distributed under [BSD 3-Clause License](https://github.com/wmde/wikibase-release-pipeline/blob/master/LICENSE). Please fulfill the requirements. It significantly simplifies deployment of a [Wikibase](https://github.com/wikimedia/Wikibase) instance. The versions of the Wikibase-related software can be found in [docker-compose.yml](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml): [wikibase:1.35-bundle](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L16), [mariadb:10.3](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L50), [wdqs:0.3.40](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L84) and [elasticsearch:6.5.4-extra](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L130). The image [wdqs:0.3.40](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/docker-compose.yml#L84) is a Wikibase specific [Blazegraph](https://blazegraph.com) image.

Copy [env.tmpl](https://github.com/UB-Mannheim/RaiseWikibase/blob/main/env.tmpl) to `.env` and substitute the default values with your
own usernames and passwords.

Install [Docker](https://docs.docker.com/get-docker/).

Run in the main RaiseWikibase folder:
```shell
docker-compose up -d
```

If it runs first time, it pulls the Wikibase Docker images. Then it builds, creates, starts, and attaches to containers for a service.
Check whether it's running using:
```shell
docker ps
```

If it's running, the output looks like this:
```shell
CONTAINER ID        IMAGE                                COMMAND                   CREATED              STATUS              PORTS                       NAMES
0cac985f00a5        wikibase/quickstatements:latest      "/bin/bash /entrypoi…"    About a minute ago   Up About a minute   0.0.0.0:9191->80/tcp        raisewikibase_quickstatements_1
2f277b599ea0        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run…"    About a minute ago   Up About a minute                               raisewikibase_wdqs-updater_1
3d7e6462b290        wikibase/wdqs-frontend:latest        "/entrypoint.sh ngin…"    About a minute ago   Up About a minute   0.0.0.0:8282->80/tcp        raisewikibase_wdqs-frontend_1
ef945d05fc88        wikibase/wikibase:1.35-bundle        "/bin/bash /entrypoi…"    About a minute ago   Up About a minute   0.0.0.0:8181->80/tcp        raisewikibase_wikibase_1
10df54332657        wikibase/wdqs-proxy                  "/bin/sh -c \"/entryp…"   About a minute ago   Up About a minute   0.0.0.0:8989->80/tcp        raisewikibase_wdqs-proxy_1
37f34328b73f        wikibase/wdqs:0.3.40                 "/entrypoint.sh /run…"    About a minute ago   Up About a minute   9999/tcp                    raisewikibase_wdqs_1
9a1c8ddd8c89        wikibase/elasticsearch:6.5.4-extra   "/usr/local/bin/dock…"    About a minute ago   Up About a minute   9200/tcp, 9300/tcp          raisewikibase_elasticsearch_1
b640eaa556e3        mariadb:10.3                         "docker-entrypoint.s…"    About a minute ago   Up About a minute   127.0.0.1:63306->3306/tcp   raisewikibase_mysql_1
```

The logs can be viewed via:
```shell
docker-compose logs -f
```

Usually in less than a minute from the start you will see the messages from `wdqs-updater_1` in the logs: `INFO  o.w.q.r.t.change.RecentChangesPoller - Got no real changes` and `INFO  org.wikidata.query.rdf.tool.Updater - Sleeping for 10 secs`. The Wikibase front-end (http://localhost:8181) and query service (http://localhost:8282) are already available. Data filling can be started.

If you want to stop the Wikibase Docker, to remove all your uploaded data and to run a fresh Wikibase instance, use:
```shell
docker-compose down
sudo rm -rf mediawiki-*  query-service-data/ quickstatements-data/
docker-compose up -d
```

See also [Wikibase/Docker](https://www.mediawiki.org/wiki/Wikibase/Docker).