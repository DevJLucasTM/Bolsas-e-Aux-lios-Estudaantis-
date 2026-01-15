-- 1. Inserindo USUÁRIOS (13 registros: 3 Servidores + 10 Estudantes)
-- Obs: Estou forçando o ID para garantir a integridade nos inserts seguintes.
INSERT INTO Usuario (Id_usuario, CPF, Nome, Email, Senha, Endereco, Telefone) VALUES
(1, '111.111.111-11', 'Ana Silva', 'ana.silva@uni.edu.br', 'senha123', 'Rua A, 100', '88 99999-1111'),
(2, '222.222.222-22', 'Bruno Souza', 'bruno.souza@uni.edu.br', 'senha123', 'Rua B, 200', '88 99999-2222'),
(3, '333.333.333-33', 'Carlos Lima', 'carlos.lima@uni.edu.br', 'senha123', 'Rua C, 300', '88 99999-3333'),
(4, '444.444.444-44', 'Daniel Alves', 'daniel.alves@aluno.uni.edu.br', 'aluno123', 'Rua D, 400', '88 99999-4444'),
(5, '555.555.555-55', 'Elena Costa', 'elena.costa@aluno.uni.edu.br', 'aluno123', 'Rua E, 500', '88 99999-5555'),
(6, '666.666.666-66', 'Fabio Dias', 'fabio.dias@aluno.uni.edu.br', 'aluno123', 'Rua F, 600', '88 99999-6666'),
(7, '777.777.777-77', 'Gabriela Rocha', 'gabriela.rocha@aluno.uni.edu.br', 'aluno123', 'Rua G, 700', '88 99999-7777'),
(8, '888.888.888-88', 'Helio Martins', 'helio.martins@aluno.uni.edu.br', 'aluno123', 'Rua H, 800', '88 99999-8888'),
(9, '999.999.999-99', 'Igor Mendes', 'igor.mendes@aluno.uni.edu.br', 'aluno123', 'Rua I, 900', '88 99999-9999'),
(10, '101.101.101-10', 'Julia Pereira', 'julia.pereira@aluno.uni.edu.br', 'aluno123', 'Rua J, 1000', '88 99999-1010'),
(11, '121.121.121-12', 'Karla Nunes', 'karla.nunes@aluno.uni.edu.br', 'aluno123', 'Rua K, 1100', '88 99999-1212'),
(12, '131.131.131-13', 'Lucas Torres', 'lucas.torres@aluno.uni.edu.br', 'aluno123', 'Rua L, 1200', '88 99999-1313'),
(13, '141.141.141-14', 'Mariana Gomes', 'mariana.gomes@aluno.uni.edu.br', 'aluno123', 'Rua M, 1300', '88 99999-1414');

-- 2. Inserindo SERVIDORES (Ids 1, 2, 3)
INSERT INTO Servidor (Id_Servidor, Cargo, Setor) VALUES
(1, 'Assistente Social', 'Assistência Estudantil'),
(2, 'Coordenador', 'Pesquisa e Extensão'),
(3, 'Professor', 'Departamento de TI');

-- 3. Inserindo FORMULÁRIOS SOCIOECONÔMICOS (Para os 10 alunos)
INSERT INTO FormularioSocioeconomico (Id_Form, Banco, Agencia, Conta, RendaPerCapita) VALUES
(1, 'Banco do Brasil', '1234-5', '11111-1', 450.00),
(2, 'Caixa', '2345-6', '22222-2', 800.00),
(3, 'Nubank', '0001', '33333-3', 1200.00),
(4, 'Inter', '0001', '44444-4', 300.00),
(5, 'Bradesco', '3456-7', '55555-5', 600.00),
(6, 'Itau', '4567-8', '66666-6', 1500.00),
(7, 'Banco do Brasil', '1234-5', '77777-7', 550.00),
(8, 'Caixa', '2345-6', '88888-8', 400.00),
(9, 'Nubank', '0001', '99999-9', 950.00),
(10, 'Santander', '5678-9', '00000-0', 1100.00);

-- 4. Inserindo ESTUDANTES (Ids 4 a 13, vinculados aos Formulários 1 a 10)
INSERT INTO Estudante (Id_Estudante, Matricula, Curso, Id_Form) VALUES
(4, '2025001', 'Sistemas de Informação', 1),
(5, '2025002', 'Engenharia de Software', 2),
(6, '2025003', 'Redes de Computadores', 3),
(7, '2025004', 'Ciência da Computação', 4),
(8, '2025005', 'Sistemas de Informação', 5),
(9, '2025006', 'Design Digital', 6),
(10, '2025007', 'Engenharia de Software', 7),
(11, '2025008', 'Redes de Computadores', 8),
(12, '2025009', 'Sistemas de Informação', 9),
(13, '2025010', 'Ciência da Computação', 10);

-- 5. Inserindo PROGRAMAS DE AUXÍLIO
INSERT INTO Programa_Auxilio (Id_programa, Nome_Programa, Descricao, Valor, Tipo, Vagas) VALUES
(1, 'Auxílio Moradia', 'Ajuda de custo para aluguel', 400.00, 'Assistência', 50),
(2, 'Bolsa Iniciação Científica', 'Pesquisa acadêmica', 700.00, 'Pesquisa', 20),
(3, 'Auxílio Alimentação', 'Isenção no RU', 0.00, 'Assistência', 100);

-- 6. Inserindo EDITAIS
INSERT INTO Edital (Id_edital, Data_inicio, Data_fim, Status, Id_programa) VALUES
(1, '2025-01-01', '2025-01-31', 'Aberto', 1), -- Moradia
(2, '2025-02-01', '2025-02-28', 'Fechado', 2), -- Pesquisa
(3, '2025-03-01', '2025-03-31', 'Aberto', 3); -- Alimentação

-- 7. Inserindo INSCRIÇÕES
-- Daniel (4) se inscreve em Moradia (Edital 1)
-- Elena (5) se inscreve em Pesquisa (Edital 2)
-- Gabriela (7) se inscreve em Moradia (Edital 1)
INSERT INTO Inscricao (Id_inscricao, Data, Status, Justificativa, Id_edital, Id_Estudante) VALUES
(1, '2025-01-05', 'Aprovado', 'Moro em outra cidade', 1, 4),
(2, '2025-02-10', 'Aprovado', 'Projeto de IA', 2, 5),
(3, '2025-01-06', 'Reprovado', 'Documentação incompleta', 1, 7),
(4, '2025-03-05', 'Em Análise', 'Baixa renda', 3, 8);

-- 8. Inserindo DOCUMENTOS (Para inscrição 1 e 2)
INSERT INTO Documento (Id_documento, Tipo_documento, Arquivo_path, Id_inscricao) VALUES
(1, 'Comprovante Residencia', '/docs/residencia_daniel.pdf', 1),
(2, 'Projeto Pesquisa', '/docs/projeto_elena.pdf', 2),
(3, 'Historico Escolar', '/docs/historico_gabriela.pdf', 3);

-- 9. Inserindo SUPERVISIONA (Servidores validando inscrições)
-- Ana (1) validou a inscrição 1 e 3 (Moradia)
-- Bruno (2) validou a inscrição 2 (Pesquisa)
INSERT INTO Supervisiona (Id_Servidor, Id_inscricao) VALUES
(1, 1),
(2, 2),
(1, 3);

-- 10. Inserindo BOLSISTA (Apenas os aprovados: Inscrição 1 e 2)
-- Daniel é bolsista de Moradia, orientado por Ana
-- Elena é bolsista de Pesquisa, orientada por Carlos (Professor)
INSERT INTO Bolsista (Id_inscricao, Data_inicio, Data_fim, Frequencia, Id_Orientador, Id_Estudante) VALUES
(1, '2025-02-01', '2025-12-31', 'Mensal', 1, 4),
(2, '2025-03-01', '2025-12-31', 'Semanal', 3, 5);

-- 11. Inserindo PAGAMENTO (Para o Bolsista da Inscrição 1)
INSERT INTO Pagamento (Id_pagamento, Valor_pago, Data_Pagamento, Id_inscricao) VALUES
(1, 400.00, '2025-03-05', 1),
(2, 400.00, '2025-04-05', 1);

-- AJUSTE DE SEQUÊNCIAS (Boas Práticas PostgreSQL)
-- Como inserimos IDs manualmente em colunas SERIAL, precisamos atualizar o contador interno
-- para que o próximo insert automático não tente usar um ID que já existe (ex: ID 1).
SELECT setval('usuario_id_usuario_seq', (SELECT MAX(Id_usuario) FROM Usuario));
SELECT setval('formulariosocioeconomico_id_form_seq', (SELECT MAX(Id_Form) FROM FormularioSocioeconomico));
SELECT setval('programa_auxilio_id_programa_seq', (SELECT MAX(Id_programa) FROM Programa_Auxilio));
SELECT setval('edital_id_edital_seq', (SELECT MAX(Id_edital) FROM Edital));
SELECT setval('inscricao_id_inscricao_seq', (SELECT MAX(Id_inscricao) FROM Inscricao));
SELECT setval('documento_id_documento_seq', (SELECT MAX(Id_documento) FROM Documento));
SELECT setval('pagamento_id_pagamento_seq', (SELECT MAX(Id_pagamento) FROM Pagamento));