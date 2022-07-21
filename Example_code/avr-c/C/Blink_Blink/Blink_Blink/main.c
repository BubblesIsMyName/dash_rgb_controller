/*
 * Blink_Blink.c
 *
 * Created: 19/04/2019 14:19:01
 * Author : GATIS
 */ 

#define F_CPU 16000000UL // 16 Mhz

#include <util/delay.h>
#include <avr/io.h>


int main(void)
{

	DDRB = 0xFF; // PORTB All output
	while (1)
	{
		PORTB = 0xFF; // Turns on all LED's
		_delay_ms(1000); // 1 second delay
		PORTB = 0x00; // Turns off all LED's
		_delay_ms(1000);
	}
}