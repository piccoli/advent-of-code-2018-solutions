#! /usr/bin/env bash
set -e -o pipefail

main() {
    local program base_name expected passed=0

    check_if_installed python3
    mkdir -p input expected_output

    for day in {01..25}; do
        program=day$day.py

        if [[ ! -f $program ]]; then
            warning "$program not found."
            continue
        fi

        for input_file in input/${day}*; do
            base_name=$(basename "$input_file")
            expected=expected_output/$base_name

            if [[ ! -f $expected ]]; then
                warning "Expected output '$expected' not found."
                continue
            fi

            printf "%10s < %-30s" "$program" "$input_file..."

            if identical <(run $day "$input_file") $expected; then
                pass
                let ++passed
            else
                fail
            fi
        done
    done

    if (( passed < 25 )); then
        abort ""
    fi
}

run() {
    local -r day=$1 file=$2
    local opts=""

    if [[ $file =~ test ]]; then
        opts+="--test"
    fi

    python3 day$day.py $opts 2>/dev/null < $file || true
}

identical() {
    local -r file_a=$1 file_b=$2
    test -z "$(diff -q "$file_a" "$file_b")"
}

pass() {
    printf "%s\n" $(colored PASS 2)
}

fail() {
    printf "%s\n" $(colored FAIL 1)
}

log() {
    message 2 Log $@
}

abort() {
    warning $@
    exit 1
}

warning() {
    message 1 Warning $@
}

message() {
    local -r color=$1
    local prompt=$2

    if [[ -n $prompt ]]; then
        prompt="[$(colored "$prompt" $color)] "
    fi

    shift 2

    printf "$prompt$@" >> /dev/stderr
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

check_if_installed() {
    while [[ $# -gt 0 ]]; do
        command -v $1 >& /dev/null || abort "utility '$1' is required but could not be found in the system! Quitting..."
        shift
    done
}

main
exit $?
