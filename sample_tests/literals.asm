COPY	START	0	.COPY FILE FROM INPUT TO OUTPUT
FIRST	STL	RETADR	.SAVE TETURN ADDRESS
	LDB	#LENGTH	.ESTABLISH BASE REGISTER
	BASE	LENGTH	
CLOOP	JSUB	RDREC	.READ INPUT RECORD
	LDA	LENGTH	.TEST FOR EOF
	COMP	#0	
	JEQ	ENDFIL	.EXIT IF EOF FOUND
	JSUB	WRREC	.WRITE OUTPUT RECORD
	J	CLOOP	
	WD	=X'0533'	.WRITE CHARACTER
	WD	=X'0556'	.WRITE CHARACTER
ENDFIL	LDA	=C'EOF'	.INSERT END OF FILE MARKER
	STA	BUFFER
	LTORG
	WD	=X'05'	.WRITE CHARACTER
	WD	=X'52'	.WRITE CHARACTER	
	LDA	#3	
	STA	LENGTH	
	JSUB	WRREC	.WRITE EOF
	J	@RETADR	.RETURN TO CALLER
	LTORG		
RETADR	RESW	1	
LENGTH	RESW	1	.LENGTH OF THE RECORD
BUFFER	RESB	4096	.4096-BYTE BUFFER AREA
BUFEND	EQU	*	
MAXLEN	EQU	BUFFEND-BUFFER	.MAXIMUM RECORD LENGTH
.			
.                  SUBROUTINE TO READ RECORD INTO BUFFER			
.			
RDREC	CLEAR	X	.CLEAR LOOP COUNTER
	CLEAR	A	.CLEAR A TO ZERO
	CLEAR	S	.CLEAR S TO ZERO
	LDT	#MAXLEN	
RLOOP	TD	INPUT	.TEST INPUT DEVICE
	JEQ	RLOOP	.LOOP UNTIL READY
	RD	INPUT	.READ CHARACTER INTO REGISTER A
	COMPR	A,S	.TEST FOR END OF RECORD (X'00')
	JEQ	EXIT	.EXIT LOOP IF EOR
	STCH	BUFFER,X	.CTORE CHARACTER IN BUFFER
	TIXR	T	.LOOP UNLESS MAX LENGTH HAS BEEN REACHED
	JLT	RLOOP	
EXIT	STX	LENGTH	.SAVE RECORD LENGTH
	RSUB		.RETURN TO CALLER
INPUT	BYTE	X'F1'	.CODE FOR INPUT DEVICE
.			
.                  SUBROUTINE TO WRITE RECORD INTO BUFFER			
.			
WRREC	CLEAR	X	.CLEAR LOOP COUNTER
	LDT	LENGTH	
WLOOP	TD	=X'05'	.TEST INPUT DEVICE
	JEQ	WLOOP	.LOOP UNTIL READY
	LDCH	BUFFER,X	.GET CHARACTER FROM BUFFER
	WD	=X'05'	.WRITE CHARACTER
	WD	=X'052'	.WRITE CHARACTER
	WD	=X'0533'	.WRITE CHARACTER
	WD	=X'05456'	.WRITE CHARACTER
	TIXR	T	.LOOP UNTIL ALL CHARACTERS HAVE BEEN WRITTEN
	JLT	WLOOP	
	RSUB		.RETURN TO CALLER
	END	FIRST	
