import zeep

from .utils import URLS, validar, trim, gera_digito_verificador


class SOAPClient:
    def __init__(self, usuario, senha, ambiente):
        """Inicializa atributos da classe SOAPClient

        Arguments:
            usuario {str} -- login de acesso do SIGEPWeb
            senha {str} -- senha de acesso do SIGEPWeb
            ambiente {int} -- ambiente a ser utilizado para as consultas (Homologacao/Producao)
        """
        self.usuario = str(usuario)
        self.senha = str(senha)
        self._ambiente = None
        self._url = None
        self.url_preco_prazo = URLS["PrecoPrazo"]
        self.ambiente = ambiente

        self.cliente = zeep.Client(self.url)
        self.clientePrecoPrazo = zeep.Client(self.url_preco_prazo)

    @property
    def ambiente(self):
        return self._ambiente

    @ambiente.setter
    def ambiente(self, value):
        """Define o ambiente e a url de consulta a ser utilizado conforma o
        ambiente escolhido (Homologação/Produção).

        Arguments:
            value {int} -- ambiente a ser utilizado durante as consultas

        Raises:
            KeyError -- Quando o ambiente fornecido não existe.
        """
        self._ambiente = value

        try:
            self._url = URLS[self._ambiente]
            self.cliente = zeep.Client(self.url)
        except KeyError:
            raise KeyError(
                "Ambiente inválido! Valor deve ser 1 para HOMOLOGACAO e 2 "
                "para PRODUCAO"
            )

    @property
    def url(self):
        """Retorna a URL do ambiente utilizado.

        Returns:
            str -- string com a url do ambiente
        """
        return self._url

    def consulta_cep(self, cep):
        """Este método retorna o endereço correspondente ao número de CEP
        informado.

        Arguments:
            cep {str} -- Número do CEP sem ponto e/ou hífen.

        Returns:
            dict -- Dict contendo os dados do endereco
        """

        param = {
            "cep": trim(cep),
        }

        validar("cep", param["cep"])

        return zeep.helpers.serialize_object(
            self.cliente.service.consultaCEP(**param), target_cls=dict
        )

    def busca_cliente(self, id_contrato, id_cartao_postagem):
        """Este método retorna os serviços disponíveis do contrato
        para um determinado cartão de postagem.

        Arguments:
            id_contrato {str} -- Número do contrato
            id_cartao_postagem {str} -- Cartão de postagem vinculado ao contrato

        Returns:
            dict -- Dict contendo os dados do contrato do clinte
        """

        params = {
            "idContrato": id_contrato,
            "idCartaoPostagem": id_cartao_postagem,
            "usuario": self.usuario,
            "senha": self.senha,
        }

        # Validamos cada ums dos parametros segundo a documentacao
        validar("idContrato", params["idContrato"])
        validar("idCartaoPostagem", params["idCartaoPostagem"])

        # Realizamos a consulta e convertermos a saida pra Dict (ao inves de um objeto)
        # Facilitando o manuseio do conteudo retornado
        return zeep.helpers.serialize_object(
            self.cliente.service.buscaCliente(**params), target_cls=dict
        )

    def verifica_disponibilidade_servico(
        self, cod_administrativo, numero_servico, cep_origem, cep_destino
    ):
        """Verifica se um serviço que não possui abrangência
        nacional está disponível entre um CEP de Origem e de Destino.

        Arguments:
            cod_administrativo {str} -- Código Administrativo do contrato do Cliente com os Correios.
            numero_servico {str} -- Códigos dos serviços contratados.
            cep_origem {str} -- Número do CEP sem ponto e/ou hífen.
            cep_destino {str} -- Número do CEP sem ponto e/ou hífen.

        Returns:
            {str} -- código do erro#motivo.
        """

        params = {
            "codAdministrativo": cod_administrativo,
            "numeroServico": numero_servico,
            "cepOrigem": trim(cep_origem),
            "cepDestino": trim(cep_destino),
            "usuario": self.usuario,
            "senha": self.senha,
        }

        # Validamos cada ums dos parametros segundo a documentacao
        validar("codAdministrativo", params["codAdministrativo"])
        validar("numeroServico", params["numeroServico"])
        validar("cep", params["cepOrigem"])
        validar("cep", params["cepDestino"])

        return self.cliente.service.verificaDisponibilidadeServico(**params)

    def get_status_cartao_postagem(self, numero_cartao_postagem):
        """Este método retorna o situação do cartão de postagem, ou seja,
        se o mesmo está 'Normal' ou 'Cancelado'. É recomendada
        a pesquisa periódica para evitar tentativa de postagens com cartão
        suspenso, ocasionando a não aceitação dos objetos nos Correios.

        Arguments:
            numero_cartao_postagem {str} -- Número do Cartão de Postagem vinculado ao contrato.

        Returns:
            str -- 'Normal' para cartão de postagem disponível, 'Cancelado' caso contrário.
        """

        params = {
            "numeroCartaoPostagem": numero_cartao_postagem,
            "usuario": self.usuario,
            "senha": self.senha,
        }

        validar("numeroCartaoPostagem", params["numeroCartaoPostagem"])

        return self.cliente.service.getStatusCartaoPostagem(**params)

    def solicita_etiquetas(
        self, tipo_destinatario, cnpj, id_servico, qtd_etiquetas
    ):
        """Retorna uma dada quantidade de etiquetas sem o digito verificador.

        Arguments:
            tipo_destinatario {str} -- Identificação com a letra “C”, de cliente
            cnpj {str} -- CNPJ da empresa.
            id_servico {int} -- Id do serviço, porderá ser obtido no método buscaCliente().
            qtd_etiquetas {int} -- Quantidade de etiquetas a serem solicitadas.

        Returns:
            list -- Lista de etiquetas
        """

        params = {
            "tipoDestinatario": tipo_destinatario,
            "identificador": trim(cnpj),
            "idServico": id_servico,
            "qtdEtiquetas": qtd_etiquetas,
            "usuario": self.usuario,
            "senha": self.senha,
        }

        validar("tipoDestinatario", params["tipoDestinatario"])
        validar("cnpj", params["identificador"])

        etiquetas_str = self.cliente.service.solicitaEtiquetas(**params)
        etiquetas_lista = etiquetas_str.split(",")

        return etiquetas_lista

    def gera_digito_verificador_etiquetas(self, etiquetas, offline=True):
        """Este método retorna o DV - Dígito Verificador de um lista de etiquetas.

        Arguments:
            etiquetas {list} -- Lista de etiquetas sem o digito verificador.

        Keyword Arguments:
            online {bool} -- indica se o dv será buscado no webservice dos correios ou gerado localmente (default: {True})

        Returns:
            list -- lista contendo os dv correspondentes as etiquetas fornecidas.
        """

        params = {
            "etiquetas": etiquetas,
            "usuario": self.usuario,
            "senha": self.senha,
        }

        for etiqueta in etiquetas:
            validar("etiqueta", etiqueta)

        if offline:
            digitos = gera_digito_verificador(params["etiquetas"])
        else:
            digitos = self.cliente.service.geraDigitoVerificadorEtiquetas(
                **params
            )

        return digitos

    def calcular_preco_prazo(
        self,
        numero_servico,
        cep_origem,
        cep_destino,
        peso,
        formato,
        comprimento,
        altura,
        largura,
        diametro,
        mao_propria,
        valor_declarado,
        aviso_recebimento,
        cod_administrativo=False,
        senha=False,
    ):

        params = {
            "nCdEmpresa": cod_administrativo or "",
            "sDsSenha": senha or "",
            "nCdServico": numero_servico,
            "sCepOrigem": cep_origem,
            "sCepDestino": cep_destino,
            "nVlPeso": peso,
            "nCdFormato": formato,
            "nVlComprimento": comprimento,
            "nVlAltura": altura,
            "nVlLargura": largura,
            "nVlDiametro": diametro,
            "sCdMaoPropria": "S" if mao_propria else "N",
            "nVlValorDeclarado": valor_declarado,
            "sCdAvisoRecebimento": "S" if aviso_recebimento else "N"
        }

        return self.clientePrecoPrazo.service.CalcPrecoPrazo(**params)

    def bloquear_objeto(self, numero_etiqueta, id_plp):
        params = {
            "numeroEtiqueta": numero_etiqueta,
            "idPlp": id_plp,
            "tipoBloqueio": "FRAUDE_BLOQUEIO",
            "acao": "DEVOLVIDO_AO_REMETENTE",
            "usuario": self.usuario,
            "senha": self.senha,
        }
        return self.cliente.service.bloquearObjeto(**params)
