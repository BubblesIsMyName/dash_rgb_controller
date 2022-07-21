/*
 * Blink_Blink.c
 *
 * Created: 19/04/2019 14:19:01
 * Author : GATIS
 */ 

#define F_CPU 16000000UL // 16 Mhz

#include <util/delay.h>
#include <avr/io.h>
#include "coms.h"

int main(void)
{
	//char Set_ch = 48;
	DDRB = 0xFF; // PORTB All output
	USART_Init();
	while (1)
	{
		if(UART_RxChar())
		{
		UART_TxChar((char)UART_RxChar());
		PORTB = 0xFF; // Turns on all LED's
		_delay_ms(1000);
		}
		PORTB = 0x00; // Turns off all LED's
		_delay_ms(1000);
	}
}

