-- 1. Tabela Usuário (Usa SERIAL para gerar o ID base)
CREATE TABLE Usuario (
    Id_usuario SERIAL PRIMARY KEY,
    CPF VARCHAR(14) UNIQUE NOT NULL,
    Nome VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Senha VARCHAR(255) NOT NULL,
    Endereco VARCHAR(255),
    Telefone VARCHAR(20)
);

-- 2. Tabela Formulário Socioeconômico
CREATE TABLE FormularioSocioeconomico (
    Id_Form SERIAL PRIMARY KEY,
    Banco VARCHAR(100),
    Agencia VARCHAR(20),
    Conta VARCHAR(20),
    RendaPerCapita DECIMAL(10, 2)
);

-- 3. Tabela Programa Auxílio
CREATE TABLE Programa_Auxilio (
    Id_programa SERIAL PRIMARY KEY,
    Nome_Programa VARCHAR(100) NOT NULL,
    Descricao TEXT,
    Valor DECIMAL(10, 2),
    Tipo VARCHAR(50),
    Vagas INT
);

-- 4. Tabela Servidor
-- Não usa SERIAL pois herda o ID de Usuario
CREATE TABLE Servidor (
    Id_Servidor INTEGER PRIMARY KEY,
    Cargo VARCHAR(100),
    Setor VARCHAR(100),
    CONSTRAINT FK_Servidor_Usuario FOREIGN KEY (Id_Servidor) REFERENCES Usuario(Id_usuario)
);

-- 5. Tabela Estudante
-- Não usa SERIAL pois herda o ID de Usuario
CREATE TABLE Estudante (
    Id_Estudante INTEGER PRIMARY KEY,
    Matricula VARCHAR(50) UNIQUE NOT NULL,
    Curso VARCHAR(100),
    Id_Form INTEGER,
    CONSTRAINT FK_Estudante_Usuario FOREIGN KEY (Id_Estudante) REFERENCES Usuario(Id_usuario),
    CONSTRAINT FK_Estudante_Form FOREIGN KEY (Id_Form) REFERENCES FormularioSocioeconomico(Id_Form)
);

-- 6. Tabela Edital
CREATE TABLE Edital (
    Id_edital SERIAL PRIMARY KEY,
    Data_inicio DATE,
    Data_fim DATE,
    Status VARCHAR(50),
    Id_programa INTEGER,
    CONSTRAINT FK_Edital_Programa FOREIGN KEY (Id_programa) REFERENCES Programa_Auxilio(Id_programa)
);

-- 7. Tabela Inscrição
CREATE TABLE Inscricao (
    Id_inscricao SERIAL PRIMARY KEY,
    Data DATE DEFAULT CURRENT_DATE, -- Adicionei DEFAULT para facilitar no Postgres
    Status VARCHAR(50),
    Justificativa TEXT,
    Id_edital INTEGER,
    Id_Estudante INTEGER,
    CONSTRAINT FK_Inscricao_Edital FOREIGN KEY (Id_edital) REFERENCES Edital(Id_edital),
    CONSTRAINT FK_Inscricao_Estudante FOREIGN KEY (Id_Estudante) REFERENCES Estudante(Id_Estudante)
);

-- 8. Tabela Documento
CREATE TABLE Documento (
    Id_documento SERIAL PRIMARY KEY,
    Tipo_documento VARCHAR(100),
    Arquivo_path VARCHAR(255),
    Data_envio DATE DEFAULT CURRENT_DATE,
    Id_inscricao INTEGER,
    CONSTRAINT FK_Documento_Inscricao FOREIGN KEY (Id_inscricao) REFERENCES Inscricao(Id_inscricao)
);

-- 9. Tabela Supervisiona
CREATE TABLE Supervisiona (
    Id_Servidor INTEGER,
    Id_inscricao INTEGER UNIQUE, -- Garante relação 1:1 conforme diagrama (U)
    PRIMARY KEY (Id_Servidor, Id_inscricao),
    CONSTRAINT FK_Supervisiona_Servidor FOREIGN KEY (Id_Servidor) REFERENCES Servidor(Id_Servidor),
    CONSTRAINT FK_Supervisiona_Inscricao FOREIGN KEY (Id_inscricao) REFERENCES Inscricao(Id_inscricao)
);

-- 10. Tabela Pagamento
CREATE TABLE Pagamento (
    Id_pagamento SERIAL PRIMARY KEY,
    Valor_pago DECIMAL(10, 2),
    Data_Pagamento DATE,
    Id_inscricao INTEGER,
    CONSTRAINT FK_Pagamento_Inscricao FOREIGN KEY (Id_inscricao) REFERENCES Inscricao(Id_inscricao)
);

-- 11. Tabela Bolsista
-- Não usa SERIAL pois a chave é a própria FK da Inscrição
CREATE TABLE Bolsista (
    Id_inscricao INTEGER PRIMARY KEY, 
    Data_inicio DATE,
    Data_fim DATE,
    Data_desligamento DATE,
    Frequencia VARCHAR(50),
    Id_Orientador INTEGER,
    Id_Estudante INTEGER,
    CONSTRAINT FK_Bolsista_Inscricao FOREIGN KEY (Id_inscricao) REFERENCES Inscricao(Id_inscricao),
    CONSTRAINT FK_Bolsista_Orientador FOREIGN KEY (Id_Orientador) REFERENCES Servidor(Id_Servidor),
    CONSTRAINT FK_Bolsista_Estudante FOREIGN KEY (Id_Estudante) REFERENCES Estudante(Id_Estudante)
);