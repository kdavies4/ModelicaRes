before="$(date +%s)"
long block of slow code
after="$(date +%s)"
elapsed_seconds="$(expr $after - $before)"
echo Elapsed time for code block: $elapsed_seconds

