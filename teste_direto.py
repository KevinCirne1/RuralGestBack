from app import app
from models.usuario import Usuario
from werkzeug.security import check_password_hash

print("\n>>> INICIANDO O TESTE DE LOGIN <<<")

try:
    with app.app_context():
        # DADOS QUE VAMOS TESTAR
        cpf_alvo = '12345678915'
        senha_teste = '123456'

        print(f"1. Buscando usuário com Login/CPF: {cpf_alvo}")
        
        # Busca no banco
        usuario = Usuario.query.filter_by(login=cpf_alvo).first()

        if not usuario:
            print("❌ ERRO CRÍTICO: Usuário NÃO encontrado no banco de dados!")
            print("   -> Verifique se o CPF digitado no cadastro foi exatamente esse.")
        else:
            print(f"✅ Usuário encontrado: {usuario.nome}")
            print(f"🔑 Hash da Senha (Banco): {usuario.senha}")
            
            # Teste de verificação
            print(f"2. Comparando com a senha digitada: '{senha_teste}'...")
            
            check_seguro = check_password_hash(usuario.senha, senha_teste)
            
            if check_seguro:
                print("\n🎉 SUCESSO TOTAL! A senha '123456' bate perfeitamente com o hash no banco.")
                print("   -> Se o login não funciona no site, o erro é no arquivo auth.py ou JavaScript.")
            else:
                print("\n💀 FALHA DE SENHA! O hash no banco NÃO corresponde a '123456'.")
                print("   -> Isso significa que a senha salva no banco é diferente da que você pensa.")
                print("   -> Solução: Delete o usuário e cadastre de novo.")

except Exception as e:
    print(f"❌ ERRO NO SCRIPT: {e}")

print(">>> FIM DO TESTE <<<\n")