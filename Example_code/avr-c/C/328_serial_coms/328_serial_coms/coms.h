
    void USART_Init()
    {
	    UCSR0B= 0x18;   // Enable Receiver and Transmitter
	    UCSR0C= 0x86;   // Asynchronous mode 8-bit data and 1-stop bit
	    UCSR0A= 0x00;   // Normal Baud rate(no doubling), Single processor commn
	    UBRR0H= 0;
	    UBRR0L= 207;     // 9600 Baud rate at 11.0592MHz
    }
	
	void UART_TxChar(char ch)
	{
		while((UCSR0A & (1<<UDRE0))==0); // Wait till Transmitter(UDR) register becomes Empty
		UDR0 =ch;             // Load the data to be transmitted
	}
	
	char UART_RxChar()
	{
		while((UCSR0A & (1<<RXC0))==0);   // Wait till the data is received
		return(UDR0);                    // return the received char
	}