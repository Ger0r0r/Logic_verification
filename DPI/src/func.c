#include <vpi_user.h>

int func_fmul_c(int a, int b) {

	vpi_printf("C mul\n%x x %x\n", a, b);

    float x = *(float*)&a;
    float y = *(float*)&b;

    float res = x * y;

	int res_like_int = *(int*)&res;
	vpi_printf("res %x\n", res_like_int);

    return res_like_int;
}