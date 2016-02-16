# -*- coding: utf-8 -*-
# #############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Michell Stuttgart
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###############################################################################

from unittest import TestCase
from sigep.sigep_exceptions import ErroCampoObrigatorio
from sigep.sigep_exceptions import ErroCampoTamanhoIncorreto
from sigep.sigep_exceptions import ErroCampoNaoNumerico
from sigep.sigep_exceptions import ErroTipoIncorreto
from sigep.campos import CampoBase
from sigep.campos import CampoString
from sigep.campos import CampoCEP
from sigep.campos import CampoBooleano


class TestCampoBase(TestCase):

    def test__validar(self):
        campo_base = CampoBase('campo_base', obrigatorio=True)
        self.assertRaises(ErroCampoObrigatorio, campo_base._validar, None)

        campo_base = CampoBase('campo_base', obrigatorio=False)
        self.assertEqual(campo_base._validar('Teste'), True)


class TestCampoString(TestCase):

    def test__formata_valor(self):
        campo_string = CampoString('campo_string')
        self.assertRaises(ErroTipoIncorreto, campo_string._formata_valor, 5)
        self.assertEqual(campo_string._formata_valor('Teste  '), 'Teste')

    def test__validar(self):

        campo_string = CampoString('campo_string', tamanho=3)
        self.assertRaises(ErroCampoTamanhoIncorreto, campo_string._validar,
                          'Teste')

        campo_string = CampoString('campo_string', tamanho=5)
        self.assertEqual(campo_string._validar('Teste'), True)


class TestCampoCEP(TestCase):

    def test__formata_valor(self):
        campo_cep = CampoCEP('campo_cep')
        self.assertRaises(ErroTipoIncorreto, campo_cep._formata_valor, 5)
        self.assertEqual(campo_cep._formata_valor('37.800-503'), '37800503')

    def test__validar(self):
        campo_cep = CampoCEP('cep')
        self.assertEqual(campo_cep._validar('37800503'), True)
        self.assertRaises(ErroCampoTamanhoIncorreto, campo_cep._validar,
                          '3780050')
        self.assertRaises(ErroCampoNaoNumerico, campo_cep._validar,
                          '378005AB')


class TestCampoBoolean(TestCase):

    def test__formata_valor(self):
        campo_bool = CampoBooleano('boolean_teste')
        self.assertEqual(campo_bool._formata_valor(True), True)
        self.assertEqual(campo_bool._formata_valor(False), False)

    def test__validar(self):
        campo_bool = CampoBooleano('boolean_teste')
        self.assertEqual(campo_bool._validar(True), True)
        self.assertRaises(ErroTipoIncorreto, campo_bool._validar, 'True')
        self.assertRaises(ErroTipoIncorreto, campo_bool._validar, 1)
