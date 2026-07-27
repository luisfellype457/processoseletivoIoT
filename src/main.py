from machine import Pin, I2C
import time

LIMITE_TEMPO_X = 5000
LIMITE_VARIACAO_Y = 3.0

led_porta = Pin(5, Pin.OUT)
led_temp = Pin(0, Pin.OUT)
btn1 = Pin(14, Pin.IN, Pin.PULL_DOWN)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

end_mpu = 0x68 #endereço do mpu no i2c

i2c.writeto_mem(end_mpu, 0x6B, b'\x00') #iniciando o mpu

def ler_temperatura():
    temp_bytes = i2c.readfrom_mem(end_mpu, 0x41, 2) #guardando temperatura em 0x41 e 0x42 (a temperatura tem 16 bits, mas só consegue guardar 8 por vez)
    temperatura = (temp_bytes[0] << 8) | temp_bytes[1]  #juntando as duas metades da leitura
    if temperatura > 32767: #verificando se é negativo
        temperatura -=65536
    temperatura = (temperatura/340.0) + 36.53 #fórmula pra converter em graus celsius
    return temperatura

porta_aberta_antes = False 
tempo_abertura = 0
temperatura_ref = ler_temperatura()

alarme_porta = False
alarme_temp = False

led_porta.value(0)
led_temp.value(0)

print("Sistema de Monitoramento Inicializado")

while True:
    porta = btn1.value() #1 - Fechada \ 0 - Aberta
    temperatura = ler_temperatura()
    
    delta = abs(temperatura - temperatura_ref) #pega a variação (positiva ou negativa)

    if not porta:
        if not porta_aberta_antes: #começa o cronômetro
            tempo_abertura = time.ticks_ms()
            porta_aberta_antes = True

        tempo = time.ticks_diff(time.ticks_ms(), tempo_abertura)

        if tempo >= LIMITE_TEMPO_X and not alarme_porta: #acende alarme da porta
            alarme_porta = True
            led_porta.value(1)
            print("ALERTA: Porta aberta por muito tempo!")

    else:
        porta_aberta_antes = False

    if delta >= LIMITE_VARIACAO_Y and not alarme_temp:  #acende alarme térmico
        alarme_temp = True
        led_temp.value(1)
        print("ALERTA: Degradacao termica detectada!")


    if porta == 1 and delta < LIMITE_VARIACAO_Y and (alarme_porta or alarme_temp):
        time.sleep(0.6)
        alarme_porta = False
        alarme_temp = False
        led_porta.value(0)
        led_temp.value(0)
        temperatura_ref = temperatura
        print("Status: Sistema Normalizado.")

    time.sleep(0.05)
