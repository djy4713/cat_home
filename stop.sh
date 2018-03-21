#!/usr/bin/env bash

ps ux | grep 'uwsgi' | grep -v grep | awk '{print $2}' | xargs kill -9
