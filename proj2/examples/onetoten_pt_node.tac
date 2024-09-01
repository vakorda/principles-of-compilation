t1 := 0
x := t1
l1:
t2 := x
t3 := 1
t2 := t2 + t3
x := t2
t4 := x
out := t4
t5 := x
t6 := 10
t5 := t5 = t6
if (t5 == 0) goto l1
halt;