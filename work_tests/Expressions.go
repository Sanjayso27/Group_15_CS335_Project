package main;

func main(){
	var x,y int = 2*2+3-4/5,0;
	print x;
	var z bool = (1<2) && (2<3) || (3<4) ;
	x -= 1;
	x -= 1;
	x *= 1;
	x /= 1;
	print x;
	var a,b int=1,2;
	a=a<<b;
	a=a>>b;
	a=a>>2;
	print a;
	var t int =1;
	print -t;
	u,v:=1,2;
	w:=a+b;
	var temp int =2;
	temp|=1;
	print temp;
	temp^=1;
	print temp;
	temp&=1;
	print temp;
	print 3|2;
	var chk int =2;
	var ptr *int = &chk;
	print 1+*ptr;
	print 1-*ptr;
	print 1* *ptr;
	print 1/ *ptr;
	*ptr+=1;
	print *ptr;
	*ptr-=1;
	print *ptr;
	*ptr*=1;
	print *ptr;
	*ptr/=1;
	print *ptr;
	print *ptr| 1;
	print *ptr& 0;
	print *ptr^ 1;
	print *ptr<< 1;
	print *ptr>> 1;
	*ptr |=1;
	print *ptr;
	*ptr &=1;
	print *ptr;
	*ptr ^=1;
	print *ptr;
	print 7%3;
};
