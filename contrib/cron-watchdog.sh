#!/bin/sh

export JOB=/etc/init.d/flightradar24

$JOB status 2>&1 >>/dev/null || $job start
