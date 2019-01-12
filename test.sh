#! /usr/bin/env bash
set -e -o pipefail

main() {
    abort_if_not_installed python3 diff

    mkdir -p input expected_output

    if [[ $# -lt 1 ]]; then
        test_all
        return $?
    else
        if ! test_day $1; then
            warning "Program for day '$1' has failed."
            return 1
        else
            log "All tests passed successfully."
            return 0
        fi
    fi
}

test_all() {
    local passed=0

    for day in {01..25}; do
        if test_day $day; then
            let ++passed
        fi
    done

    if (( passed < 25 )); then
        warning "One or more programs failed, see above."
    else 
        log "All tests passed successfully."
    fi

    test $passed -eq 25
}

test_day() {
    local -r day=$1
    local -r program=day$day.py

    local program base_name expected failed=0

    if [[ ! -f $program ]]; then
        warning "$program not found."
        return 2
    fi

    for input_file in input/${day}*; do
        base_name=$(basename "$input_file")

        expected=expected_output/$base_name

        if [[ ! -f $expected ]]; then
            warning "Expected output file '$expected' not found or not a file."
            continue
        fi

        printf "%10s < %-20s" "$program" "$input_file..."

        if identical <(run $day "$input_file") $expected; then
            pass
        else
            fail
            let ++failed
        fi
    done

    test $failed -eq 0
}

run() {
    local -r day=$1 file=$2
    local options=""

    if [[ $file =~ test ]]; then
        options+="--test"
    fi

    python3 day$day.py $options 2>/dev/null < $file
}

identical() {
    local -r file_a=$1 file_b=$2
    diff -q "$file_a" "$file_b" &>/dev/null
}

pass() {
    printf "%s\n" $(colored PASS 2)
}

fail() {
    printf "%s\n" $(colored FAIL 1)
}

abort_if_not_installed() {
    while [[ $# -gt 0 ]]; do
        command -v $1 >& /dev/null\
            || abort "utility '$1' is required, but could not be found in the system. Aborting..."
        shift
    done
}

abort() {
    warning "$@"
    exit 1
}

warning() {
    message 1 Warning "$@"
}

log() {
    message 2 Log "$@"
}

message() {
    local -r color=$1
    local prompt=$2

    if [[ -n $prompt ]]; then
        prompt="[$(colored "$prompt" $color)] "
    fi

    shift 2

    printf "$prompt$@\n" >> /dev/stderr
}

colored() {
    local text=$1 color=""
    local -r fg=$2 bg=$3

    if [[ -n $fg && -n $bg ]]; then
        color="\e[3${fg};4${bg}m"
    elif [[ -n $fg ]]; then
        color="\e[3${fg}m"
    elif [[ -n $bg ]]; then
        color="\e[4${bg}m"
    fi

    printf "$color$text\e[0m"
}

main $@
exit $?
