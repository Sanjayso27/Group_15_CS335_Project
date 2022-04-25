global main
extern printf
extern scanf
section .data
    temp dq 0
    print_int db "%i ", 0x00
    farray_print db "%f ", 0x0a, 0x00
    scan_int db "%d", 0
section .text
main:
    push ebp
    mov ebp, esp
    sub esp, 864
    mov edi, 2
    mov [ebp-4], edi
    mov edi, 2
    mov [ebp-8], edi
    mov edi, [ebp-4]
    mov esi, [ebp-8]
    imul edi, esi
    mov [ebp-12], edi
    mov edi, 3
    mov [ebp-16], edi
    mov edi, [ebp-12]
    mov esi, [ebp-16]
    add edi, esi
    mov [ebp-20], edi
    mov edi, 4
    mov [ebp-24], edi
    mov edi, 5
    mov [ebp-28], edi
    xor edx, edx
    mov eax, [ebp-24]
    mov ebx, [ebp-28]
    idiv ebx
    mov [ebp-32], eax
    mov edi, [ebp-20]
    mov esi, [ebp-32]
    sub edi ,esi
    mov [ebp-36], edi
    mov edi, 0
    mov [ebp-40], edi
    mov edi, [ebp-36]
    mov [ebp-44], edi
    mov edi, [ebp-40]
    mov [ebp-48], edi
    mov esi, [ebp-44]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-52], edi
    mov edi, 2
    mov [ebp-56], edi
    mov edi, [ebp-52]
    mov esi, [ebp-56]
    xor eax, eax
    cmp edi, esi
    setl al
    mov [ebp-60], eax
    mov edi, 2
    mov [ebp-64], edi
    mov edi, 3
    mov [ebp-68], edi
    mov edi, [ebp-64]
    mov esi, [ebp-68]
    xor eax, eax
    cmp edi, esi
    setl al
    mov [ebp-72], eax
    mov edi, [ebp-60]
    mov esi, [ebp-72]
    and edi, esi
    mov [ebp-76], edi
    mov edi, 3
    mov [ebp-80], edi
    mov edi, 4
    mov [ebp-84], edi
    mov edi, [ebp-80]
    mov esi, [ebp-84]
    xor eax, eax
    cmp edi, esi
    setl al
    mov [ebp-88], eax
    mov edi, [ebp-76]
    mov esi, [ebp-88]
    or edi, esi
    mov [ebp-92], edi
    mov edi, [ebp-92]
    mov [ebp-96], edi
    mov edi, 1
    mov [ebp-100], edi
    mov edi, [ebp-44]
    mov esi, [ebp-100]
    sub edi ,esi
    mov [ebp-44], edi
    mov edi, 1
    mov [ebp-104], edi
    mov edi, [ebp-44]
    mov esi, [ebp-104]
    sub edi ,esi
    mov [ebp-44], edi
    mov edi, 1
    mov [ebp-108], edi
    mov edi, [ebp-44]
    mov esi, [ebp-108]
    imul edi, esi
    mov [ebp-44], edi
    mov edi, 1
    mov [ebp-112], edi
    xor edx, edx
    mov eax, [ebp-44]
    mov ebx, [ebp-112]
    idiv ebx
    mov [ebp-44], eax
    mov esi, [ebp-44]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-116], edi
    mov edi, 2
    mov [ebp-120], edi
    mov edi, [ebp-116]
    mov [ebp-124], edi
    mov edi, [ebp-120]
    mov [ebp-128], edi
    mov edi, [ebp-124]
    mov cl, [ebp-128]
    shl edi, cl
    mov [ebp-132], edi
    mov edi, [ebp-132]
    mov [ebp-124], edi
    mov edi, [ebp-124]
    mov cl, [ebp-128]
    shr edi, cl
    mov [ebp-136], edi
    mov edi, [ebp-136]
    mov [ebp-124], edi
    mov edi, 2
    mov [ebp-140], edi
    mov edi, [ebp-124]
    mov cl, [ebp-140]
    shr edi, cl
    mov [ebp-144], edi
    mov edi, [ebp-144]
    mov [ebp-124], edi
    mov esi, [ebp-124]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-148], edi
    mov edi, [ebp-148]
    mov [ebp-152], edi
    mov esi, [ebp-152]
    mov edi, 0
    sub edi, esi
    mov [ebp-156], edi
    mov esi, [ebp-156]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-160], edi
    mov edi, 2
    mov [ebp-164], edi
    mov edi, [ebp-160]
    mov [ebp-168], edi
    mov edi, [ebp-164]
    mov [ebp-172], edi
    mov edi, [ebp-124]
    mov esi, [ebp-128]
    add edi, esi
    mov [ebp-176], edi
    mov edi, [ebp-176]
    mov [ebp-180], edi
    mov edi, 2
    mov [ebp-184], edi
    mov edi, [ebp-184]
    mov [ebp-188], edi
    mov edi, 1
    mov [ebp-192], edi
    mov edi, [ebp-188]
    mov esi, [ebp-192]
    or edi, esi
    mov [ebp-188], edi
    mov esi, [ebp-188]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-196], edi
    mov edi, [ebp-188]
    mov esi, [ebp-196]
    xor edi, esi
    mov [ebp-188], edi
    mov esi, [ebp-188]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-200], edi
    mov edi, [ebp-188]
    mov esi, [ebp-200]
    and edi, esi
    mov [ebp-188], edi
    mov esi, [ebp-188]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 3
    mov [ebp-204], edi
    mov edi, 2
    mov [ebp-208], edi
    mov edi, [ebp-204]
    mov esi, [ebp-208]
    or edi, esi
    mov [ebp-212], edi
    mov esi, [ebp-212]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 2
    mov [ebp-216], edi
    mov edi, [ebp-216]
    mov [ebp-220], edi
    lea edi, [ebp-220]
    mov [ebp-224], edi
    mov edi, [ebp-224]
    mov [ebp-228], edi
    mov edi, 1
    mov [ebp-232], edi
    mov esi, ebp
    add esi, -236
    mov ebx, [ebp-228]
    mov cx, 1
loop1:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop1
    mov edi, [ebp-232]
    mov esi, [ebp-236]
    add edi, esi
    mov [ebp-240], edi
    mov esi, [ebp-240]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-244], edi
    mov esi, ebp
    add esi, -248
    mov ebx, [ebp-228]
    mov cx, 1
loop2:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop2
    mov edi, [ebp-244]
    mov esi, [ebp-248]
    sub edi ,esi
    mov [ebp-252], edi
    mov esi, [ebp-252]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-256], edi
    mov esi, ebp
    add esi, -260
    mov ebx, [ebp-228]
    mov cx, 1
loop3:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop3
    mov edi, [ebp-256]
    mov esi, [ebp-260]
    imul edi, esi
    mov [ebp-264], edi
    mov esi, [ebp-264]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 1
    mov [ebp-268], edi
    mov esi, ebp
    add esi, -272
    mov ebx, [ebp-228]
    mov cx, 1
loop4:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop4
    xor edx, edx
    mov eax, [ebp-268]
    mov ebx, [ebp-272]
    idiv ebx
    mov [ebp-276], eax
    mov esi, [ebp-276]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -280
    mov ebx, [ebp-228]
    mov cx, 1
loop5:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop5
    mov edi, 1
    mov [ebp-284], edi
    mov edi, [ebp-284]
    mov esi, [ebp-228]
    add [esi], edi
    mov esi, ebp
    add esi, -288
    mov ebx, [ebp-228]
    mov cx, 1
loop6:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop6
    mov esi, [ebp-288]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -292
    mov ebx, [ebp-228]
    mov cx, 1
loop7:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop7
    mov edi, 1
    mov [ebp-296], edi
    mov edi, [ebp-296]
    mov esi, [ebp-228]
    sub [esi], edi
    mov esi, ebp
    add esi, -300
    mov ebx, [ebp-228]
    mov cx, 1
loop8:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop8
    mov esi, [ebp-300]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -304
    mov ebx, [ebp-228]
    mov cx, 1
loop9:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop9
    mov edi, 1
    mov [ebp-308], edi
    mov edi, [ebp-308]
    mov esi, [ebp-228]
    imul edi, [esi]
    mov [esi], edi
    mov esi, ebp
    add esi, -312
    mov ebx, [ebp-228]
    mov cx, 1
loop10:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop10
    mov esi, [ebp-312]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -316
    mov ebx, [ebp-228]
    mov cx, 1
loop11:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop11
    mov edi, 1
    mov [ebp-320], edi
    mov edi, [ebp-320]
    mov esi, [ebp-228]
    xor edx, edx
    mov eax, [esi]
    idiv edi
    mov [esi], eax
    mov esi, ebp
    add esi, -324
    mov ebx, [ebp-228]
    mov cx, 1
loop12:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop12
    mov esi, [ebp-324]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -328
    mov ebx, [ebp-228]
    mov cx, 1
loop13:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop13
    mov edi, 1
    mov [ebp-332], edi
    mov edi, [ebp-328]
    mov esi, [ebp-332]
    or edi, esi
    mov [ebp-336], edi
    mov esi, [ebp-336]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -340
    mov ebx, [ebp-228]
    mov cx, 1
loop14:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop14
    mov edi, 0
    mov [ebp-344], edi
    mov edi, [ebp-340]
    mov esi, [ebp-344]
    and edi, esi
    mov [ebp-348], edi
    mov esi, [ebp-348]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -352
    mov ebx, [ebp-228]
    mov cx, 1
loop15:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop15
    mov edi, 1
    mov [ebp-356], edi
    mov edi, [ebp-352]
    mov esi, [ebp-356]
    xor edi, esi
    mov [ebp-360], edi
    mov esi, [ebp-360]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -364
    mov ebx, [ebp-228]
    mov cx, 1
loop16:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop16
    mov edi, 1
    mov [ebp-368], edi
    mov edi, [ebp-364]
    mov cl, [ebp-368]
    shl edi, cl
    mov [ebp-372], edi
    mov esi, [ebp-372]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -376
    mov ebx, [ebp-228]
    mov cx, 1
loop17:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop17
    mov edi, 1
    mov [ebp-380], edi
    mov edi, [ebp-376]
    mov cl, [ebp-380]
    shr edi, cl
    mov [ebp-384], edi
    mov esi, [ebp-384]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -388
    mov ebx, [ebp-228]
    mov cx, 1
loop18:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop18
    mov edi, 1
    mov [ebp-392], edi
    mov edi, [ebp-392]
    mov esi, [ebp-228]
    or [esi], edi
    mov esi, ebp
    add esi, -396
    mov ebx, [ebp-228]
    mov cx, 1
loop19:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop19
    mov esi, [ebp-396]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -400
    mov ebx, [ebp-228]
    mov cx, 1
loop20:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop20
    mov edi, 1
    mov [ebp-404], edi
    mov edi, [ebp-404]
    mov esi, [ebp-228]
    and [esi], edi
    mov esi, ebp
    add esi, -408
    mov ebx, [ebp-228]
    mov cx, 1
loop21:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop21
    mov esi, [ebp-408]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, ebp
    add esi, -412
    mov ebx, [ebp-228]
    mov cx, 1
loop22:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop22
    mov edi, 1
    mov [ebp-416], edi
    mov edi, [ebp-416]
    mov esi, [ebp-228]
    xor [esi], edi
    mov esi, ebp
    add esi, -420
    mov ebx, [ebp-228]
    mov cx, 1
loop23:
    mov edx, [ebx]
    mov [esi], edx
    add esi, 4
    add ebx, 4
    dec cx
    jnz loop23
    mov esi, [ebp-420]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov edi, 7
    mov [ebp-424], edi
    mov edi, 3
    mov [ebp-428], edi
    xor edx, edx
    mov eax, [ebp-424]
    mov ebx, [ebp-428]
    idiv ebx
    mov [ebp-432], edx
    mov esi, [ebp-432]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esp, ebp
    pop ebp
    ret
