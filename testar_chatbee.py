from app.services.chatbee import enviar_alerta_chatbee

print("Iniciando teste de disparo do Chatbee...")

# Simulando uma lista de servidores que caíram
servidores_teste = ["TESTE-01", "TESTE-02"]

sucesso = enviar_alerta_chatbee(servidores_teste)

if sucesso:
    print("\n✅ Teste concluído! O alerta deve ter chegado no WhatsApp configurado.")
else:
    print("\n❌ Falha no teste. Verifique os logs acima e confira se o seu TOKEN e URL do Chatbee estão corretos no .env.")
