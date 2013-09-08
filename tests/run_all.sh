#bin/sh

for test in `find -name '*.py' -executable`; do
    echo Running $test
    ./$test;
done
