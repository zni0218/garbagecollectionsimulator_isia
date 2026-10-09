Simulador de Recolha de Resíduos Urbanos com Aprendizagem por Reforço

 Sobre o projeto

Este projeto foi desenvolvido no âmbito da unidade curricular Introdução a Sistemas Inteligentes e Autónomos, durante o terceiro ano da Licenciatura em Inteligência Artificial e Ciência de Dados.

O objetivo consiste em desenvolver um simulador de recolha de resíduos urbanos no qual agentes autónomos aprendem a tomar decisões e a planear rotas de recolha eficientes num ambiente urbano gerado aleatoriamente.

Utilizando Python, foi implementado um sistema capaz de gerar cidades com diferentes configurações numa grelha, criando cenários que permitem testar e avaliar o comportamento dos agentes em diferentes condições.

 Aprendizagem por Reforço

Foram desenvolvidos agentes que utilizam técnicas de Aprendizagem por Reforço (Reinforcement Learning) para aprender a tomar decisões durante o processo de recolha de resíduos.

Através da interação com o ambiente simulado, os agentes aprendem estratégias de navegação e seleção de rotas, procurando melhorar o desempenho da recolha de acordo com o sistema de recompensas definido.

Esta abordagem permite estudar a aplicação de aprendizagem automática a problemas de planeamento, navegação e otimização em ambientes dinâmicos.

 Sistema Multiagente e Comunicação Descentralizada

Os agentes foram implementados utilizando a framework SPADE, que permite desenvolver sistemas multiagente em Python.

O sistema segue uma arquitetura descentralizada, na qual os agentes comunicam e coordenam as suas ações sem depender de um único agente central responsável por todas as decisões.

Para suportar esta comunicação, foi implementado o protocolo ControlNET, responsável por estabelecer as regras de comunicação entre os agentes.

Esta componente permite explorar a coordenação entre agentes autónomos e a aplicação de sistemas inteligentes distribuídos a um problema urbano.

 Ambiente de Simulação

O simulador gera cidades com configurações aleatórias representadas numa grelha, permitindo avaliar os agentes em diferentes cenários de recolha.

A utilização de ambientes gerados automaticamente facilita a realização de experiências e a comparação do comportamento dos agentes perante diferentes configurações.

 Experiências e Resultados

O projeto inclui várias funcionalidades, experiências e resultados que permitem analisar o funcionamento do simulador e o comportamento dos agentes.

Para uma descrição detalhada da arquitetura, das funcionalidades implementadas, das experiências realizadas e dos resultados obtidos, consulta o documento PDF disponibilizado neste repositório.

 Tecnologias utilizadas

Python — implementação do simulador e da lógica dos agentes.

Reinforcement Learning — aprendizagem de estratégias de decisão e planeamento de rotas.

SPADE — desenvolvimento e execução dos agentes autónomos.

ControlNET — protocolo de comunicação implementado no âmbito do projeto.

Sistemas Multiagente — coordenação descentralizada de agentes autónomos.
 
 Objetivos de aprendizagem

Este projeto permitiu explorar a aplicação de técnicas de Inteligência Artificial a um problema de otimização urbana, combinando aprendizagem por reforço, sistemas multiagente, comunicação entre agentes e simulação.

Representa uma abordagem prática ao desenvolvimento de sistemas autónomos capazes de aprender, tomar decisões e coordenar ações num ambiente partilhado.

 Documentação

O documento PDF incluído no repositório apresenta uma descrição aprofundada do projeto, incluindo as funcionalidades implementadas, os detalhes técnicos, as experiências realizadas e os resultados obtidos.