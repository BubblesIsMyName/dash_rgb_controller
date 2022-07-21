;
; PWM.asm
; CHAPTER 1: A PAUSE ROUTINE
; Created: 09/12/2018 15:28:58
; Author : GATIS
;

.DEF A = R16 ;General Purpose acumulator
.DEF I = R20 ;INDEX
.DEF N = R22 ;COUNTER
.ORG 0000 ;Indicates that we want our program at the bottom of mem (since we have no interupts)

ON_RESET:
	SBI DDRB,5 ;Set Port be as outputs
;In the main loop we fiko the 0 bit of the Port B with an SBI command, then call the oause routine, all in a loop that goes around forever.
MAIN_LOOP:
	SBI PINB,5 ;Flip the zero bit
	RCALL PAUSE ;WAIT/PAUSE
	RJMP MAIN_LOOP ;Go back and do it again
;The next two subroutines waste time so we can see the LED blinking
;Both routines load zero into a register then repeatedly subtracts one 
;until it hits zero again (subtracting one from zero gives 255)

PAUSE: LDI N,0 ;Do Nothing Loop loads 0s to the R20 register
PLUPE: 	RCALL MPAUSE ;Calls another do nothing loop
		DEC N ;Decrements R20, Check if we come back to zero
		BRNE PLUPE ;Branch if not equal to zero, so if N hasn't reached zero yet, goes back to PLUPE
		RET	;Return from call
MPAUSE: LDI I,0 ;START at zero
MPLUP:	DEC I ;Subtract one
		BRNE MPLUP ;Keep Looping until we hit zero
		RET ;Return from CALL