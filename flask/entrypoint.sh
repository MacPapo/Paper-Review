#!/usr/bin/env sh
echo "EXECUTE FLASK DB UPGRADE" && flask db upgrade
flask run
