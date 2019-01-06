#! /usr/bin/gawk -f

function to_regs(x) {
    #return sprintf("regs[%s]", x == IP ? "IP" : x)
    x = int(x)
    return sprintf("%s", x == IP ? "ip" : Variable[x + 1])
}

function convert(name, a, b, c) {
    if (name ~ /add|mul|ban|bor|setr|gtr|eqr/)
        a = to_regs(a)

    if (name ~ /addr|mulr|banr|borr|gtir|gtrr|eqir|eqrr/)
        b = to_regs(b)

    if (a == "ip") a = "" (NR - 2)
    if (b == "ip") b = "" (NR - 2)

    c = to_regs(c)

    return name ~ /setr|seti/ ? sprintf("l%-3d:\n    %s = %s;", NR - 2, c, a)\
                              : sprintf("l%-3d:\n    %s = %s %s %s;", NR - 2, c, a, Operator[name], b)
}

BEGIN {
    print "#include <stdio.h>\n"
    #print "#define IP " IP "\n"
    print "int main(void) {"
    #print "    int regs[] = { 0, 0, 0, 0, 0, 0 };\n"
    print "    int a, b, c, d, e, f, ip;\n"

    split("abcdef", Variable, "")

    Operator["addr"] = "+"
    Operator["addi"] = "+"
    Operator["mulr"] = "*"
    Operator["muli"] = "*"
    Operator["banr"] = "&"
    Operator["bani"] = "&"
    Operator["borr"] = "|"
    Operator["bori"] = "|"
    Operator["gtir"] = ">"
    Operator["gtri"] = ">"
    Operator["gtrr"] = ">"
    Operator["eqri"] = "=="
    Operator["eqir"] = "=="
    Operator["eqrr"] = "=="
}

/#ip/ { IP = int($2); next }

{ print convert($1, $2, $3, $4) }

END {
    print "\n    return 0;"
    print "}"
}
