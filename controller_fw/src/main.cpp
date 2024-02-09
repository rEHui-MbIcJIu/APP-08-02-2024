#include <Arduino.h>
#include <AccelStepper.h>
#include <Servo.h>

#define PIN_X_STEP PIN_PD7
#define PIN_X_DIR PIN_PC5
#define PIN_X_END PIN_PC2

#define PIN_Y_STEP PIN_PC6
#define PIN_Y_DIR PIN_PC7
#define PIN_Y_END PIN_PC3

#define PIN_Z_EN PIN_PB1
#define PIN_Z_IN1 PIN_PB2
#define PIN_Z_IN2 PIN_PB3
#define PIN_Z_END PIN_PC4

#define PIN_LED PIN_PD5

#define PIN_SERVO PIN_PB7

#define SERVO_OPEN 140
#define SERVO_OPEN_WIDE 120
#define SERVO_CLOSE 150

AccelStepper stp_x(AccelStepper::DRIVER, PIN_X_STEP, PIN_X_DIR);
AccelStepper stp_y(AccelStepper::DRIVER, PIN_Y_STEP, PIN_Y_DIR);

Servo servo;

static void xy_home(void);
static void xy_move(uint32_t x, uint32_t y);
static void xy_go_to_item(uint8_t item_n, bool camera);

static void z_home(void);
static void z_move(void);

void setup() {
    Serial.begin(115200);

    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, HIGH);
    delay(200);
    digitalWrite(PIN_LED, LOW);

    servo.attach(PIN_SERVO);
    servo.write(SERVO_OPEN_WIDE);

    pinMode(PIN_Z_EN, OUTPUT);
    digitalWrite(PIN_Z_EN, LOW);
    pinMode(PIN_Z_IN1, OUTPUT);
    digitalWrite(PIN_Z_IN1, LOW);
    pinMode(PIN_Z_IN2, OUTPUT);
    digitalWrite(PIN_Z_IN2, LOW);

    pinMode(PIN_X_END, INPUT);
    pinMode(PIN_Y_END, INPUT);

    stp_x.setMaxSpeed(3000.f);
    stp_x.setAcceleration(10000.f);
    stp_y.setMaxSpeed(3000.f);
    stp_y.setAcceleration(10000.f);

    Serial.println("START");
}

void loop() {
    if(Serial.available() > 0) {
        char cmd_byte = Serial.read();

        digitalWrite(PIN_LED, LOW);

        if(cmd_byte == 'H') {
            servo.write(SERVO_OPEN);
            z_home();
            xy_home();

            Serial.println("OK");
        } else if((cmd_byte == 'M') || (cmd_byte == 'C')) {
            while(Serial.available() < 1)
                ;
            uint8_t item_n = Serial.read() - '0';
            bool camera = (cmd_byte == 'C');
            xy_go_to_item(item_n, camera);
            if(camera) {
                digitalWrite(PIN_LED, HIGH);
            }
            Serial.println("OK");
        } else if(cmd_byte == 'T') {
            servo.write(SERVO_CLOSE);
            delay(500);
            servo.write(SERVO_OPEN);
            delay(500);
            z_move();
            servo.write(SERVO_CLOSE);
            delay(500);
            z_home();

            Serial.println("OK");
        } else if(cmd_byte == 'P') {
            z_home();
            xy_go_to_item(0, false);
            servo.write(SERVO_OPEN_WIDE);
            delay(500);

            Serial.println("OK");
        }
    }
}

static void xy_home(void) {
    if(digitalRead(PIN_X_END) == 0) {
        stp_x.setCurrentPosition(0);
        stp_x.moveTo(640 * 5);
        while(stp_x.distanceToGo() != 0) {
            stp_x.run();
        }
    }

    stp_x.setSpeed(-2000.f);
    while(1) {
        if(digitalRead(PIN_X_END) == 0) {
            stp_x.setCurrentPosition(0);
            stp_x.stop();
            break;
        }
        stp_x.runSpeed();
    }

    if(digitalRead(PIN_Y_END) == 0) {
        stp_y.setCurrentPosition(0);
        stp_y.moveTo(640 * 5);
        while(stp_y.distanceToGo() != 0) {
            stp_y.run();
        }
    }

    stp_y.setSpeed(-2000.f);
    while(1) {
        if(digitalRead(PIN_Y_END) == 0) {
            stp_y.setCurrentPosition(640 * 3);
            stp_y.stop();
            break;
        }
        stp_y.runSpeed();
    }
}

static void xy_move(uint32_t x, uint32_t y) {
    stp_x.moveTo(x);
    stp_y.moveTo(y);

    while((stp_x.distanceToGo() != 0) || (stp_y.distanceToGo() != 0)) {
        stp_x.run();
        stp_y.run();
    }
}

static void xy_go_to_item(uint8_t item_n, bool camera) {
    uint32_t x_pos = 0 + (item_n / 3) * 35200;
    uint32_t y_pos = 0 + (item_n % 3) * 35200;

    if(camera) {
        x_pos += 0;
    }

    xy_move(x_pos, y_pos);
}

static void z_home(void) {
    digitalWrite(PIN_Z_IN1, LOW);
    digitalWrite(PIN_Z_IN2, HIGH);

    digitalWrite(PIN_Z_EN, HIGH);

    while(digitalRead(PIN_Z_END) != 0)
        ;

    digitalWrite(PIN_Z_EN, LOW);
}

static void z_move(void) {
    digitalWrite(PIN_Z_IN1, HIGH);
    digitalWrite(PIN_Z_IN2, LOW);

    digitalWrite(PIN_Z_EN, HIGH);

    delay(800);

    digitalWrite(PIN_Z_EN, LOW);
}