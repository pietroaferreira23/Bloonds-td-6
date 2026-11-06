# Defensores do Vale

Um jogo original do gênero Tower Defense, desenvolvido em Python com Pygame.

## Sobre o jogo

O objetivo é posicionar torres pelo mapa para impedir que os inimigos percorram o caminho e cheguem ao final.

### Recursos
- Menu principal e seleção de mapas.
- Três mapas diferentes.
- Três torres: Arqueiro, Mago e Canhão.
- Inimigos organizados em ondas.
- Melhorias e venda de torres.
- Sistema de moedas e vidas.
- Pausa e controle de velocidade.
- Salvamento local do progresso.

## Requisitos

- Python 3.10 ou superior.
- Biblioteca Pygame.

## Como executar

Abra o terminal na pasta do jogo e execute:

```bash
python -m pip install pygame
python defensores_do_vale_completo.py
```

## Controles

- Clique nos botões para escolher e posicionar torres.
- Clique em uma torre para selecioná-la.
- ESPAÇO: iniciar a próxima onda.
- P ou ESC: pausar ou continuar.
- Teclas 1, 2 ou 3: mudar a velocidade.
- TAB: alternar o alvo da torre selecionada.
- F2: mostrar ou ocultar o alcance.
- F11: alternar tela cheia.

## Gerar EXE no Windows

1. Instale Python no Windows.
2. Coloque o arquivo `.py` e `criar_exe_windows.bat` na mesma pasta.
3. Execute o arquivo `.bat`.
4. O executável será criado na pasta `dist`.

**Observação:** o arquivo `.py` é o código-fonte. Para executá-lo, é necessário Python ou outro ambiente compatível.

## Salvamento

O jogo cria o arquivo `perfil_defensores.json` para guardar o progresso.

## Projeto

Defensores do Vale é um protótipo original e independente.
