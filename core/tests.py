from django.test import TestCase


class PaginasPrincipalesTests(TestCase):
	def test_pagina_de_inicio(self):
		response = self.client.get('/', HTTP_HOST='localhost')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Plataforma de Encuestas')

	def test_pagina_404_personalizada(self):
		response = self.client.get('/ruta-inexistente/', HTTP_HOST='localhost')

		self.assertEqual(response.status_code, 404)
		self.assertContains(response, 'Recurso no encontrado', status_code=404)
