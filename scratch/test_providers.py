import asyncio

from core.provider import GeminiProvider, OpenAICompatibleProvider, ProviderFactory


async def test_providers():
    print("--- Verificando Instanciação de Provedores ---")
    try:
        # Testar Gemini (mesmo que sem chave válida, a classe deve ser instanciável)
        print("Testando instanciar GeminiProvider...")
        GeminiProvider(api_key="test")
        print("GeminiProvider instanciado com sucesso.")
    except Exception as e:
        print(f"ERRO ao instanciar GeminiProvider: {e}")

    try:
        print("\nTestando instanciar OpenAICompatibleProvider...")
        OpenAICompatibleProvider(api_key="test")
        print("OpenAICompatibleProvider instanciado com sucesso.")
    except Exception as e:
        print(f"ERRO ao instanciar OpenAICompatibleProvider: {e}")

    print("\n--- Verificando Factory ---")
    try:
        # type type: analise
        providers = await ProviderFactory.get_best_provider_for_task("analise")
        print(f"Provedores encontrados para 'analise': {[p.name for p in providers]}")
    except Exception as e:
        print(f"ERRO na Factory: {e}")

if __name__ == "__main__":
    asyncio.run(test_providers())
