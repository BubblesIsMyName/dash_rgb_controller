/*
 * Copyright 2012 Alan Burlison, alan@bleaklow.com.  All rights reserved.
 * Use is subject to license terms.
 *
 * Demo of the WS2811 driver, driving 3 pixels.
 */

#include <avr/io.h>
#include <util/delay.h>
#include <WS2811.h>
#include <string.h>

#define BIT(B)           (0x01 << (uint8_t)(B))
#define SET_BIT_HI(V, B) (V) |= (uint8_t)BIT(B)
#define SET_BIT_LO(V, B) (V) &= (uint8_t)~BIT(B)

#define PAUSE  1000     // msec
#define DELAY    20	// msec
 
// Define the output function, using pin 0 on port b.
DEFINE_WS2811_FN(WS2811RGB, PORTB, 0)
// 255,0,0,0,0,255,0,255,0  -> red, blue , green

// variables for the serial coms
const unsigned int numChars = 600;
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;

// variables for the led strip length and defaults
const byte no_of_led = 46;
const byte frame_size = 3;
const unsigned int color_array_len = no_of_led*frame_size;
// int color_values[strip_len] = {255,255,255,255,255,255};
int color_values[color_array_len];

void setup(){
    // Configure pin for output.
    SET_BIT_HI(DDRB, 0);
    SET_BIT_LO(PORTB, 0);

    Serial.begin(9600);
    Serial.println("<Arduino is ready>");

    RGB_t rgb[no_of_led];
        for (int i=0,j=0; i < color_array_len; i+=frame_size,j++) {
            rgb[j].g = 255;
            rgb[j].r = 255;
            rgb[j].b = 255;
        }
    WS2811RGB(rgb, ARRAYLEN(rgb));
    _delay_ms(DELAY);

}

// Drive the three pixels in an infinit loop.
void loop(void)
{
    recvWithEndMarker();
    if (newData){
        parseData();
        RGB_t rgb[no_of_led];
            for (int i=0,j=0; i < color_array_len; i+=frame_size,j++) {
                rgb[j].g = color_values[i]; 
                rgb[j].r = color_values[i+1]; 
                rgb[j].b = color_values[i+2]; 
            }
        WS2811RGB(rgb, ARRAYLEN(rgb));
        _delay_ms(DELAY);
    } 

}


void recvWithEndMarker() {
    static unsigned int ndx = 0;
    char endMarker = '\n';
    char rc;
 
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();
        Serial.print(rc);
        if (rc != endMarker) {
            receivedChars[ndx] = rc;
            ndx++;
            if (ndx >= numChars) {
                ndx = numChars - 1;
            }
        }
        else {
            receivedChars[ndx] = '\0'; // terminate the string
            ndx = 0;
            newData = true;
        }
    }
}

void parseData(){
    char *token; 
    int index = 0;
    token = strtok(receivedChars, ",");  // delimiters, semicolon

    while (token != NULL){
        color_values[index] = atoi(token); // Convert string data to numbers
        token = strtok(NULL, ",");
        index++;
    }
    newData = false;
}
