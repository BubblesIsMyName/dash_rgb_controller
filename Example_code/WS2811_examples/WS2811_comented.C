/*
 * Copyright 2012 Alan Burlison, alan@bleaklow.com.  All rights reserved.
 * Use is subject to license terms.
 */

/*
 * WS2811 RGB LED driver.
 */

#ifndef WS2811_h
#define WS2811_h

// RGB value structure.
typedef struct __attribute__ ((__packed__)) {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} RGB_t;

#ifndef ARRAYLEN
#define ARRAYLEN(A) (sizeof(A) / sizeof(A[0]))
#endif

/*
 * Inline asm macro to output 24-bit RGB value in (G,R,B) order, MSBit first.
 * 0 bits are 250ns hi, 1000ns lo, 1 bits are 1000ns hi, 250ns lo.
 * r18 = red byte to be output
 * r19 = green byte to be output
 * r20 = blue byte to be output
 * r26 = saved SREG
 * r27 = inner loop counter
 */


#define WS2811(PORT, PIN, RGB, LEN) \
asm volatile( \
/* initialise */ \
// The cp (compare) and cpc (compare and carry) compare the 4 things presented and then go to the conditional statement if true.
// A and B are constants
"    cp %A[len], r1      ; check len > 0, return immediately if it is\n" \
"    cpc %B[len], r1\n" \
//he instructions CP, CPI, SUB or SUBI, the branch will occur if and only if the unsigned or signed binary number represented in Rd was not equal to the unsigned or signed binary number represented in Rr.
"    brne 1f\n" \
//so if not equal moves to rjmp, which moves to the end of code, I imagine this is in a case when the input is the same
"    rjmp 16f\n" \
"1:  ld r18, Z+           ; load in first red byte to be output\n" \
"    ld r19, Z+           ; load in first green byte to be output\n" \
"    ld r20, Z+           ; load in first blue byte to be output\n" \
"    ldi r27, 8           ; load inner loop counter\n" \
"    in r26, __SREG__     ; timing-critical, so no interrupts\n" \
// CLI - Clear Global Interrupt Flag
"    cli\n" \


/* green - loop over 8 bits */ \
// sbi  - Sets a specified bit in an I/O register.
"2:  sbi  %[port], %[pin] ; pin lo -> hi\n" \
// if Bit in Register is Cleared skip (PC ← PC + 2, Skip a one word instruction)
"    sbrc r19, 7          ; tests if bit 7 in R19 is clear\n" \
"    rjmp 3f              ; if bit 7 is not clear, skip pin hi -> lo\n" \
"    cbi  %[port], %[pin] ; if bit 7 is clear, pin hi -> lo\n" \
"3:  sbrc r19, 7          ; equalise delay of both code paths\n" \
"    rjmp 4f\n" \
"4:  nop                  ; pulse timing delay\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    lsl r19              ; shift to next bit\n" \
"    dec r27              ; decrement loop counter\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    brne 2b\n            ; loop if required\n" \
"    ldi r27, 7           ; reload inner loop counter\n" \

/* red - loop over first 7 bits */ \
"5:  sbi %[port], %[pin]  ; pin lo -> hi\n" \
"    sbrc r18, 7          ; tests if bit 7 in R18 is clear\n" \
"    rjmp 6f              ; if bit 7 is not clear, skip pin hi -> lo\n" \
"    cbi %[port], %[pin]  ; false, pin hi -> lo\n" \
"6:  sbrc r18, 7          ; equalise delay of both code paths\n" \
"    rjmp 7f\n" \
"7:  nop                  ; pulse timing delay\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    lsl r18              ; shift to next bit\n" \
"    dec r27              ; decrement inner loop counter\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    brne 5b              ; inner loop, if required\n" \
"    nop                  ; equalise delay of both code paths\n" \
/* red, 8th bit - output & fetch next values */ \
"    sbi %[port], %[pin]  ; pin lo -> hi\n" \
"    sbrc r18, 7          ; test hi bit clear\n" \
"    rjmp 8f              ; true, skip pin hi -> lo\n" \
"    cbi %[port], %[pin]  ; false, pin hi -> lo\n" \
"8:  sbrc r18, 7          ; equalise delay of both code paths\n" \
"    rjmp 9f\n" \
"9:  nop                  ; pulse timing delay\n" \
"    nop\n" \
"    nop\n" \
"    ld r18, Z+           ; load next red byte\n" \
"    ld r19, Z+           ; load next green byte\n" \
"    ldi r27, 7           ; reload inner loop counter\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    nop                  ; pulse timing delay\n" \
"    nop\n" \
/* blue - loop over first 7 bits */ \
"10:  sbi %[port], %[pin] ; pin lo -> hi\n" \
"    sbrc r20, 7          ; test hi bit clear\n" \
"    rjmp 11f             ; true, skip pin hi -> lo\n" \
"    cbi %[port], %[pin]  ; false, pin hi -> lo\n" \
"11: sbrc r20, 7          ; equalise delay of both code paths\n" \
"    rjmp 12f\n" \
"12: nop                  ; pulse timing delay\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    nop\n" \
"    lsl r20              ; shift to next bit\n" \
"    dec r27              ; decrement inner loop counter\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    brne 10b             ; inner loop, if required\n" \
"    nop                  ; equalise delay of both code paths\n" \
/* blue, 8th bit -  output & handle outer loop */ \
"    sbi %[port], %[pin]  ; pin lo -> hi\n" \
"    sbrc r20, 7          ; test hi bit clear\n" \
"    rjmp 13f             ; true, skip pin hi -> lo\n" \
"    cbi %[port], %[pin]  ; false, pin hi -> lo\n" \
"13: sbrc r20, 7          ; equalise delay of both code paths\n" \
"    rjmp 14f\n" \
"14: nop                  ; pulse timing delay\n" \
"    nop\n" \
"    ldi r27, 8           ; reload inner loop counter\n" \
"    sbiw %A[len], 1      ; decrement outer loop counter\n" \
"    breq 15f             ; exit outer loop if zero\n" \
"    ld r20, Z+           ; load in next blue byte\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    rjmp 2b              ; outer loop, if required\n" \
"15: nop                  ; pulse timing delay\n" \
"    cbi %[port], %[pin]  ; pin hi -> lo\n" \
"    nop                  ; pulse timing delay\n" \
"    nop\n" \
"    out __SREG__, r26    ; reenable interrupts\n" \
"16:\n" \
: \
// INPUT OPERAND LIST
: [rgb] "z" (RGB), \
// "w" special upper register pairs r24;r26;r28;r30
  [len] "w" (LEN), \
  [port] "I" (_SFR_IO_ADDR(PORT)), \
  [pin] "I" (PIN) \
: "r18", "r19", "r20", "r26", "r27", "cc", "memory" \
)

/*
 * Define a C function to wrap the inline WS2811 macro for a given port and pin.
 */

// Wrapper for the asm macro is a macro itself
// That only takes the PORT number and the PIN number
//
#define DEFINE_WS2811_FN(NAME, PORT, PIN) \

// external declaration of the function
extern void NAME(const RGB_t *rgb, uint16_t len) __attribute__((noinline)); \


void NAME(const RGB_t *rgb, uint16_t len) { WS2811(PORT, PIN, rgb, len); }

#endif /* WS2811_h */
