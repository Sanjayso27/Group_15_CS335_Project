import struct

class CodeGenerator:
    def __init__(self,node,parser):
        self.asmCode = []
        self.asmCode.append('global main')
        self.asmCode.append('extern printf')
        self.asmCode.append('extern scanf')
        self.asmCode.append('section .data')
        #these are used in printing and scanning
        self.asmCode.append('temp dq 0')
        self.asmCode.append('print_int db "%i ", 0x00')
        self.asmCode.append('farray_print db "%f ", 0x0a, 0x00')
        self.asmCode.append('scan_int db "%d", 0')

        self.asmCode.append('section .text')
        self.parser = parser
        self.code = node.code
        self.scopeInfo = node.scopeInfo
        self.counter = 0
        self.codeIndex = 0

    def startFunc(self):
        self.asmCode.append('push ebp')
        self.asmCode.append('mov ebp, esp')

    def endFunc(self):
        self.asmCode.append('mov esp, ebp')
        self.asmCode.append('pop ebp')
        self.asmCode.append('ret')

    def getCode(self):
        while self.codeIndex < len(self.code):
            funcName = self.code[self.codeIndex][0].split(':')
            funcScope = self.parser.symbolTables[0].functions[funcName[0]]
            self.asmCode.append(funcName[0]+':')
            self.startFunc()
            self.asmCode.append('sub esp, '+str(self.parser.getWidth(funcScope) - self.parser.getParamWidth(funcScope) + self.parser.symbolTables[funcScope].metadata['total_offset']))
            self.codeIndex +=1

            while self.codeIndex < len(self.code):
                curr = self.code[self.codeIndex]
                if (len(curr) == 1 and curr[0][-2:] == '::'):
                    break
                code_ = self.genCode(self.codeIndex, funcScope)
                # print(self.codeIndex,curr)
                if len(code_) == 0:
                    if len(self.code[self.codeIndex]) != 1:
                        #return value needs to be updated in eax
                        retValOffset = self.offset(self.code[self.codeIndex][1], self.scopeInfo[self.codeIndex][1], funcScope)
                        # lea moves the addr offset in eax
                        self.asmCode.append('lea eax, [ebp'+str(retValOffset) + ']')
                    self.endFunc()
                else :
                    if code_[0] != 'none':
                        self.asmCode += code_
                self.codeIndex += 1

            self.endFunc()

        return self.asmCode

    def offset(self,ident,identScope,funcScope):
        paramSize = self.parser.getParamWidth(funcScope)

        offset = 0
        if 'is_arg' in self.parser.symbolTables[identScope].symbolTable[ident]:
            offset = 8 + paramSize - self.parser.symbolTables[identScope].symbolTable[ident]['size'] - self.parser.symbolTables[identScope].symbolTable[ident]['offset']
            # print(paramSize,self.parser.symbolTables[identScope].symbolTable[ident]['size'],self.parser.symbolTables[identScope].symbolTable[ident]['offset'])
        else :
            offset = -(self.parser.symbolTables[identScope].symbolTable[ident]['offset'] + self.parser.symbolTables[identScope].symbolTable[ident]['size'] - paramSize)
        # print(self.parser.symbolTables[identScope].symbolTable[ident]['offset'])
        if offset >=0:
            return '+'+str(offset)
        return str(offset)

    
    def genCode(self,idx,funcScope):
        instr = self.code[idx]
        scopeInfo = self.scopeInfo[idx]

        if instr[0] == 'return':
            return []
        if len(instr) == 1:
            if instr[0][-1:]==":":
                return [instr[0]]
            return [instr[0]+":"]
        if instr[0] == "array*":
            return self.arrayOffset(instr, scopeInfo, funcScope)
        if instr[0] == "array+":
            return self.arrayAccess(instr, scopeInfo, funcScope)
        if instr[0] == "struct+":
            return self.structAccess(instr,scopeInfo,funcScope)
        if instr[0] in ['+int',"*int"]:
            return self.addSubMulop(instr, scopeInfo, funcScope)
        if instr[0] == '+float':
            return self.faddSub_op(instr, scopeInfo, funcScope)
        if instr[0] == '-float':
            if len(instr) == 4:
                return self.faddSub_op(instr, scopeInfo, funcScope)
            else:
                return self.unary_fminus(instr, scopeInfo, funcScope)
        if instr[0] == '-int':
            if len(instr) == 4:
                return self.addSubMulop(instr, scopeInfo, funcScope)
            else:
                return self.unary_minus(instr, scopeInfo, funcScope)
        if instr[0] == '*float':
            return self.fmul_op(instr, scopeInfo, funcScope)
        if instr[0] == '/int':
            return self.div_op(instr, scopeInfo, funcScope)
        if instr[0] == "%" :
            return self.modulo_op(instr, scopeInfo, funcScope)
        if instr[0] == '/float':
            return self.fdiv_op(instr, scopeInfo, funcScope)
        if instr[0] == '=':
            if instr[1][0] == '*':
                return self.pointer_assign(instr, scopeInfo, funcScope)
            return self.assign_op(instr, scopeInfo, funcScope)
        if instr[0] in ["+=","-=","*=","/="]:
            return self.gen_assign_op(instr, scopeInfo, funcScope)
        if instr[0] in ['==int', '!=int', '<=int', '>=int', '>int', '<int']:
            return self.relops_cmp(instr, scopeInfo, funcScope)
        if instr[0] in ['==float', '!=float', '<=float', '>=float', '>float', '<float']:
            return self.relops_fcmp(instr, scopeInfo, funcScope)
        if instr[0] == '||':
            return self.logical_or(instr, scopeInfo, funcScope)
        if instr[0] == '&&':
            return self.logical_and(instr, scopeInfo, funcScope)
        if instr[0] in ['--', '++']:
            return self.inc_dec(instr, scopeInfo, funcScope)
        if instr[0] == 'print_int':
            return self.print_int(instr, scopeInfo, funcScope)
        if instr[0] == 'print_float':
            return self.print_float(instr, scopeInfo, funcScope)
        if instr[0] == 'scan_int':
            return self.scan_int(instr, scopeInfo, funcScope)
        if instr[0] == 'if':
            return self.if_op(instr, scopeInfo, funcScope)
        if instr[0] in ['goto','break_goto','continue_goto']:
            return ['jmp ' + instr[1]]
        if instr[0] == 'call':
            # function call
            return ['call '+instr[1]]
        if instr[0] == 'param_base':
            return self.param_base(instr, scopeInfo, funcScope)
        if instr[0] == 'param_complex':
            return self.param_complex(instr, scopeInfo, funcScope)
        if instr[0] == 'retval':
            return self.getRetVal(instr, scopeInfo, funcScope)
        if instr[0] =='|':
            return self.bitwise_or(instr,scopeInfo,funcScope)
        if instr[0] =='^':
            return self.bitwise_xor(instr,scopeInfo,funcScope)
        if instr[0] == '<<':
            return self.leftShift(instr,scopeInfo,funcScope)
        if instr[0] == '>>':
            return self.rightShift(instr,scopeInfo,funcScope)
        if instr[0] in ['&=','|=','^=']:
            return self.gen_bitwise_assign_op(instr,scopeInfo,funcScope)
        if instr[0] == '*pointer':
            return self.assign_ptr(instr, scopeInfo, funcScope)
        if instr[0][0] == '&':
            if len(instr)==3:
                return self.ampersand_op(instr, scopeInfo, funcScope)
            else :
                return self.bitwise_and(instr,scopeInfo,funcScope)

    def checkRef(self,instr,scopeInfo):
        flag = [0 for x in instr]
        for i in range(len(instr)):
            try:
                if 'reference' in self.parser.symbolTables[scopeInfo[i]].get(instr[i]):
                    flag[i] = 1
            except:
                pass
        return flag

    def structAccess(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        objOffset = self.offset(src1, scopeInfo[2], funcScope)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        code_ = []
        if flag[2] == 1:
            code_.append('mov edx, [ebp'+str(objOffset)+']')
        # a.x
        else :
            code_.append('mov edx, '+str(objOffset))
        code_.append('mov esi, ' + str(src2))
        if flag[3] == 1:
            code_.append('mov esi, [esi]')
        code_.append('add edx, esi')
        if flag[2] == 1:
            code_.append('mov esi, 0')
        else:
            code_.append('mov esi, ebp')
        code_.append('add esi, edx')
        code_.append('mov [ebp' + str(dstOffset) + '], esi')
        return code_
        
    def arrayAccess(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        objOffset = self.offset(src1, scopeInfo[2], funcScope)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code_ = []
        # for nD array access
        if flag[2] == 1:
            code_.append('mov edx, [ebp'+str(objOffset)+']')
            # dont add ebp
        else:
            code_.append('mov edx, '+str(objOffset))
        code_.append('mov esi, [ebp'+str(src2Offset)+']')
        if flag[3] == 1:
            code_.append('mov esi, [esi]')
        code_.append('add edx, esi')

        if flag[2] == 1:
            code_.append('mov esi, 0')
        else:
            code_.append('mov esi, ebp')
        code_.append('add esi, edx')
        code_.append('mov [ebp' + str(dstOffset) + '], esi')
        return code_

    def arrayOffset(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)

        code = []
        code.append('mov esi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov esi, [esi]')
        code.append('mov edi, ' + str(src2))
        code.append('imul esi, edi')

        if flag[1] == 1:
            code.append('mov edi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [edi], esi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], esi')
        return code


    def bitwise_and(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))

        code.append('and edi, esi')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code
    
    def bitwise_or(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))
        
        code.append('or edi, esi')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code
    
    def bitwise_xor(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))

        code.append('xor edi, esi')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def leftShift(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if isinstance(scopeInfo[3], int):
            code.append('mov cl, [ebp' + str(src2Offset) + ']')
            # if flag[3] == 1:
            #     code.append('mov esi, [esi]')
        else:
            code.append('mov cl, ' + str(src2))

        code.append('shl edi, cl')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def rightShift(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if isinstance(scopeInfo[3], int):
            code.append('mov cl, [ebp' + str(src2Offset) + ']')
            # if flag[3] == 1:
            #     code.append('mov esi, [esi]')
        else:
            code.append('mov cl, ' + str(src2))

        code.append('shr edi, cl')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code
    # |=
    def gen_bitwise_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.bitwise_assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        if instr[0]=="|=":
            return self.bitwise_or(instr, scopeInfo, funcScope)
        elif instr[0]=="&=":
            return self.bitwise_and(instr, scopeInfo, funcScope)
        elif instr[0]=="^=":
            return self.bitwise_xor(instr, scopeInfo, funcScope)
    # *x |= y
    def bitwise_assign_op_ptr(self, instr, scopeInfo, funcScope):
        dst = instr[1][1:]
        src = instr[2]
        # *x |= y or *x &= y or *x ^= y
        code = []
        instr[1] = dst
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)
        code.append('mov edi, [ebp' + srcOffset + ']')
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if instr[0] == '|=':
            code.append('or [esi], edi')
        elif instr[0] == '&=':
            code.append('and [esi], edi')
        elif instr[0] == '^=':
            code.append('xor [esi], edi')
        return code

    def unary_minus(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src = instr[2]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)

        code = []
        code.append('mov esi, [ebp' + str(srcOffset) + ']')
        if flag[2] == 1:
            code.append('mov esi, [esi]')
        code.append('mov edi, 0')
        code.append('sub edi, esi')
        code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code
    
    # !f stands for big-endian float
    # formats into padded format
    def binary(self,num):
        return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

    
    def unary_fminus(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src = instr[2]

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)
        binaryCode = self.binary(float(0.0))
        code = []
        code.append('mov edi, 0b' + str(binaryCode))
        code.append('mov [ebp' + str(dstOffset) + '], edi')
        code.append('fld dword [ebp' + str(dstOffset) + ']')
        code.append('fsub dword [ebp' + str(srcOffset) + ']')
        code.append('fstp dword [ebp' + str(dstOffset) + ']')
        return code

    def addSubMulop(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        # print(dstOffset,src1Offset,src2Offset)
        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')

        if isinstance(scopeInfo[3], int):
            code.append('mov esi, [ebp' + str(src2Offset) + ']')
            if flag[3] == 1:
                code.append('mov esi, [esi]')
        else:
            code.append('mov esi, ' + str(src2))

        if(instr[0][0]=="+"):
            code.append('add edi, esi')
        elif instr[0][0]=="*":
            code.append('imul edi, esi')
        else :
            code.append("sub edi ,esi")

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def faddSub_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []

        code.append('fld dword [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            if(instr[0]=="+float"):
                code.append('fadd dword [ebp' + str(src2Offset) + ']')
            else :
                code.append('fsub dword [ebp' + str(src2Offset) + ']')
        else:
            binaryCode = self.binary(float(src2))

            code.append('mov edi, 0b' + str(binaryCode))
            code.append('mov [ebp' + str(dstOffset) + '], edi')
            if(instr[0]=="+float"):
                code.append('fadd dword [ebp' + str(dstOffset) + ']')
            else :
                code.append('fsub dword [ebp+' + str(dstOffset) + ']')

        code.append('fstp dword [ebp' + str(dstOffset) + ']')
        return code
    
    def fmul_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld dword [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('fmul dword [ebp' + str(src2Offset) + ']')
        else:
            binaryCode = self.binary(float(src2))

            code.append('mov edi, 0b' + str(binaryCode))
            code.append('mov [ebp' + str(dstOffset) + '], edi')
            code.append('fmul dword [ebp' + str(dstOffset) + ']')
        code.append('fstp dword [ebp' + str(dstOffset) + ']')
        return code

    def div_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        # the 32 SB are also involved in division
        code.append('xor edx, edx')
        code.append('mov eax, [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('mov ebx, [ebp' + str(src2Offset) + ']')
        else:
            code.append('mov ebx, ' + str(src2))
        code.append('idiv ebx')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], eax')
        return code

    def modulo_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)
        code = []
        # the 32 SB are also involved in division
        code.append('xor edx, edx')
        code.append('mov eax, [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('mov ebx, [ebp' + str(src2Offset) + ']')
        else:
            code.append('mov ebx, ' + str(src2))
        code.append('idiv ebx')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edx')
        return code


    def fdiv_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        if isinstance(scopeInfo[3], int):
            src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld dword [ebp' + str(src1Offset) + ']')
        if isinstance(scopeInfo[3], int):
            code.append('fdiv dword [ebp' + str(src2Offset) + ']')
        else:
            binaryCode = self.binary(float(src2))
            code.append('mov edi, 0b' + str(binaryCode))
            code.append('mov [ebp' + str(dstOffset) + '], edi')
            code.append('fdiv dword [ebp' + str(dstOffset) + ']')
        code.append('fstp dword [ebp' + str(dstOffset) + ']')
        return code

    # *ptr =1
    def pointer_assign(self, instr, scopeInfo, funcScope):
        dst = instr[1][1:]
        src = instr[2]
        code = []
        instr[1] = dst
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)
        # print(flag)
        code.append('mov edi, [ebp' + srcOffset + ']')
        if flag[2] == 1:
            code.append('mov edi [edi]')
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('mov [esi], edi')
        return code

    def assign_op(self, instr, scopeInfo, funcScope):

        dst = instr[1]
        src = instr[2]
        code = []
        flag = self.checkRef(instr, scopeInfo)
        # print(flag)
        
        data_ = self.parser.symbolTables[scopeInfo[1]].get(instr[1])
        baseType = self.parser.getBaseType(data_['type'])
        # print(baseType)
        # handling assigning struct to other structures
        if baseType[0] in ['struct', 'array']:
            offset1 = self.offset(instr[1], scopeInfo[1], funcScope)
            offset2 = self.offset(instr[2], scopeInfo[2], funcScope)

            self.counter += 1
            label = 'loop' + str(self.counter)
            iters = int(data_['size'] / 4)
            code_ = ['mov esi, ebp', 'mov ebx, ebp']
            code_.append('add esi, '+offset1)
            code_.append('add ebx, '+offset2)
            if flag[2] == 1:
                code_.append('mov ebx, [ebp' + offset2 + ']')
            if flag[1] == 1:
                code_.append('mov esi, [ebp' + offset1 + ']')
            code_.append('mov cx, '+str(iters))
            code_.append(label + ':')
            code_.append('mov edx, [ebx]')
            code_.append('mov [esi], edx')
            code_.append('add esi, 4')
            code_.append('add ebx, 4')
            code_.append('dec cx')
            code_.append('jnz '+label)
            return code_
        
        if baseType == ['float']:
            if isinstance(scopeInfo[2], int):
                dstOffset = self.offset(dst, scopeInfo[1], funcScope)
                srcOffset = self.offset(src, scopeInfo[2], funcScope)
                code.append('fld dword [ebp' + srcOffset + ']')
                code.append('fstp dword [ebp' + dstOffset + ']')
            else:
                dstOffset = self.offset(dst, scopeInfo[1], funcScope)
                # print(float(src))
                binaryCode = self.binary(float(src))
                code.append('mov edi, 0b' + str(binaryCode))
                # moving whatever is stored in ebp + dstOffset in edi
                code.append('mov [ebp' + dstOffset + '], edi')
        else:
            if isinstance(scopeInfo[2], int):
                dstOffset = self.offset(dst, scopeInfo[1], funcScope)
                srcOffset = self.offset(src, scopeInfo[2], funcScope)
                code.append('mov edi, [ebp' + srcOffset + ']')
                if flag[2] == 1:
                    code.append('mov edi, [edi]')
                # this is for cases like a[0]=1 or assigning struct.next = &
                if flag[1] == 1:
                    code.append('mov esi, [ebp'+ str(dstOffset) + ']')
                    code.append('mov [esi], edi')
                else:
                    code.append('mov [ebp' + str(dstOffset) + '], edi')
            else:
                dstOffset = self.offset(dst, scopeInfo[1], funcScope)
                code.append('mov edi, ' + str(src))
                if flag[1] == 1:
                    code.append('mov esi, [ebp'+ str(dstOffset) + ']')
                    code.append('mov [esi], edi')
                else:
                    code.append('mov [ebp' + str(dstOffset) + '], edi')

        return code

    # +=
    def gen_assign_op(self, instr, scopeInfo, funcScope):
        if instr[1][0] == '*':
            return self.assign_op_ptr(instr, scopeInfo, funcScope)
        instr.insert(2,instr[1])
        scopeInfo.insert(2, scopeInfo[1])
        if instr[0]=="+=":
            return self.addSubMulop(instr, scopeInfo, funcScope)
        elif instr[0]=="-=":
            return self.addSubMulop(instr, scopeInfo, funcScope)
        elif instr[0]=="*=":
            return self.addSubMulop(instr, scopeInfo, funcScope)
        else :
            return self.div_op(instr, scopeInfo, funcScope)

    # *x +=y
    def assign_op_ptr(self, instr, scopeInfo, funcScope):
        dst = instr[1][1:]
        src = instr[2]
        # *x += y
        code = []
        instr[1] = dst
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)
        code.append('mov edi, [ebp' + srcOffset + ']')
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        if instr[0] == '+=':
            code.append('add [esi], edi')
        elif instr[0] == '-=':
            code.append('sub [esi], edi')
        elif instr[0] == '*=':
            code.append('imul edi, [esi]')
            code.append('mov [esi], edi')
        elif instr[0] == '/=':
            code.append('xor edx, edx')
            code.append('mov eax, [esi]')
            code.append('idiv edi')
            code.append('mov [esi], eax')
        return code

    # dereferencing a pointer
    def assign_ptr(self, instr, scopeInfo, funcScope):
        sz = self.parser.symbolTables[scopeInfo[1]].get(instr[1])['size']
        flag = self.checkRef(instr, scopeInfo)
        # print(sz,flag)
        offset1 = self.offset(instr[1], scopeInfo[1], funcScope)
        offset2 = self.offset(instr[2], scopeInfo[2], funcScope)

        self.counter += 1
        label = 'loop' + str(self.counter)
        iters = int(sz / 4)
        # modified here
        code_ = ['mov esi, ebp']
        code_.append('add esi, '+offset1)
        # modified here
        code_.append('mov ebx, [ebp' + offset2 + ']')
        if flag[2] == 1:
            code_.append('mov ebx, [ebp' + offset2 + ']')
            code_.append('mov ebx, [ebx]')
        if flag[1] == 1:
            code_.append('mov esi, [ebp' + offset1 + ']')
        code_.append('mov cx, '+str(iters))
        code_.append(label + ':')
        code_.append('mov edx, [ebx]')
        code_.append('mov [esi], edx')
        code_.append('add esi, 4')
        code_.append('add ebx, 4')
        code_.append('dec cx')
        code_.append('jnz '+label)
        return code_


    def ampersand_op(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src = instr[2]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        srcOffset = self.offset(src, scopeInfo[2], funcScope)
        code = []

        if flag[2] == 1:
            code.append('mov edi, [ebp'+ srcOffset +']')
        else:
            code.append('lea edi, [ebp'+ srcOffset +']')

        if flag[1] == 1:
            code.append('mov esi, [ebp' + dstOffset + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp'+dstOffset+'], edi')

        return code

    def relops_cmp(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        if flag[3] == 1:
            code.append('mov esi, [esi]')
        code.append('xor eax, eax')
        code.append('cmp edi, esi')
        if instr[0] == '==int':
            code.append('sete al')
        elif instr[0] == '!=int':
            code.append('setne al')
        elif instr[0] == '<int':
            code.append('setl al')
        elif instr[0] == '>int':
            code.append('setg al')
        elif instr[0] == '<=int':
            code.append('setle al')
        elif instr[0] == '>=int':
            code.append('setge al')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        # is value stored in eax 0 then why this instruction
        else:
            code.append('mov [ebp' + str(dstOffset) + '], eax')
        return code

    def relops_fcmp(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('fld dword [ebp' + str(src1Offset) + ']')
        code.append('fld dword [ebp' + str(src2Offset) + ']')
        code.append('xor eax, eax')
        code.append('fcomip')
        code.append('fstp dword [temp]')
        # al refers to the lower 8 bytes of eax register
        if instr[0] == '==float':
            code.append('sete al')
        elif instr[0] == '!=float':
            code.append('setne al')
        elif instr[0] == '<float':
            code.append('setl al')
        elif instr[0] == '>float':
            code.append('setg al')
        elif instr[0] == '<=float':
            code.append('setle al')
        elif instr[0] == '>=float':
            code.append('setge al')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], eax')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], eax')
        return code

    def print_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.offset(src, scopeInfo[1], funcScope)
        flag = self.checkRef(instr, scopeInfo)
        code = []
        # print(flag,srcOffset)
        code.append('mov esi, [ebp' + srcOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('push esi')
        code.append('push print_int')
        code.append('call printf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def print_float(self, instr, scopeInfo, funcScope):
        src = instr[1]
        srcOffset = self.offset(src, scopeInfo[1], funcScope)
        code = []
        code.append('fld dword [ebp' + srcOffset + ']')
        code.append('fstp qword [temp]')
        code.append('push dword [temp+4]')
        code.append('push dword [temp+4]')
        code.append('push dword farray_print')
        code.append('call printf')
        code.append('add esp, 12')

        return code

    def scan_int(self, instr, scopeInfo, funcScope):
        src = instr[1]
        flag = self.checkRef(instr, scopeInfo)
        srcOffset = self.offset(src, scopeInfo[1], funcScope)
        code = []
        code.append('lea esi, [ebp' + srcOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        code.append('push esi')
        code.append('push scan_int')
        code.append('call scanf')
        code.append('pop esi')
        code.append('pop esi')
        return code

    def param_base(self, instr, scopeInfo, funcScope):
        flag = self.checkRef(instr, scopeInfo)
        offset = self.offset(instr[1], scopeInfo[1], funcScope)
        if flag[1] == 1:
            return [
                'mov edx, [ebp' + offset + ']',
                'mov edx, [edx]',
                'push edx',
            ]
        else:
            return ['mov edx, [ebp' + offset + ']', 'push edx']

    def param_complex(self, instr, scopeInfo, funcScope):
        data_ = self.parser.symbolTables[scopeInfo[1]].get(instr[1])
        flag = self.checkRef(instr, scopeInfo)
        offset = self.offset(instr[1], scopeInfo[1], funcScope)
        self.counter += 1
        label = 'loop' + str(self.counter)
        iters = int(data_['size'] / 4)
        code_ = ['mov esi, ebp']
        code_.append('add esi, '+offset)
        if flag[1] == 1:
            code_.append('mov esi, [ebp'+offset+']')
        code_.append('add esi, ' + str(data_['size'] - 4))
        code_.append('mov cx, '+str(iters))
        code_.append(label + ':')
        code_.append('mov edx, [esi]')
        code_.append('push edx')
        code_.append('sub esi, 4')
        code_.append('dec cx')
        code_.append('jnz '+label)
        return code_

    def getRetVal(self, instr, scopeInfo, funcScope):
        data_ = self.parser.symbolTables[scopeInfo[1]].get(instr[1])
        offset = self.offset(instr[1], scopeInfo[1], funcScope)

        self.counter += 1
        label = 'loop' + str(self.counter)
        iters = int(data_['size'] / 4)
        code_ = ['mov esi, ebp']
        code_.append('add esi, '+offset)
        # cx is iteration count registers
        code_.append('mov cx, '+str(iters))
        code_.append(label + ':')
        code_.append('mov edx, [eax]')
        code_.append('mov [esi], edx')
        code_.append('add esi, 4')
        code_.append('add eax, 4')
        code_.append('dec cx')
        code_.append('jnz '+label)
        return code_

    def if_op(self, instr, scopeInfo, funcScope):
        var = instr[1]
        jLabel = instr[3]
        code = []
        flag = self.checkRef(instr, scopeInfo)

        varOffset = self.offset(var, scopeInfo[1], funcScope)
        # print(varOffset)
        code.append('mov edi, [ebp' + varOffset + ']')
        if flag[1] == 1:
            code.append('mov edi, [edi]')
        code.append('cmp edi, 0')
        code.append('je ' + jLabel)

        return code

    def logical_or(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        if flag[3] == 1:
            code.append('mov esi, [esi]')

        code.append('or edi, esi')

        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def logical_and(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        src1 = instr[2]
        src2 = instr[3]
        flag = self.checkRef(instr, scopeInfo)

        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        src1Offset = self.offset(src1, scopeInfo[2], funcScope)
        src2Offset = self.offset(src2, scopeInfo[3], funcScope)

        code = []
        code.append('mov edi, [ebp' + str(src1Offset) + ']')
        if flag[2] == 1:
            code.append('mov edi, [edi]')
        code.append('mov esi, [ebp' + str(src2Offset) + ']')
        if flag[3] == 1:
            code.append('mov esi, [esi]')
        code.append('and edi, esi')
        if flag[1] == 1:
            code.append('mov esi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [esi], edi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], edi')
        return code

    def inc_dec(self, instr, scopeInfo, funcScope):
        dst = instr[1]
        dstOffset = self.offset(dst, scopeInfo[1], funcScope)
        flag = self.checkRef(instr, scopeInfo)

        code = []
        code.append('mov esi, [ebp' + dstOffset + ']')
        if flag[1] == 1:
            code.append('mov esi, [esi]')
        if instr[0] == '++':
            code.append('inc esi')
        else:
            code.append('dec esi')

        if flag[1] == 1:
            code.append('mov edi, [ebp'+ str(dstOffset) + ']')
            code.append('mov [edi], esi')
        else:
            code.append('mov [ebp' + str(dstOffset) + '], esi')
        return code
