import re
from django.core.exceptions import ValidationError


class SenhaSuperForteValidator:
    def validate(self, password, user=None):
        # 1. Mínimo de 8 caracteres
        if len(password) < 8:
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")

        # 2. Letras maiúsculas e minúsculas
        if not re.search(r'[A-Z]', password):
            raise ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("A senha deve conter pelo menos uma letra minúscula.")

        # 3. Números
        if not re.search(r'[0-9]', password):
            raise ValidationError("A senha deve conter pelo menos um número.")

        # 4. Caracteres Especiais
        if not re.search(r'[@#%&!*^~?]', password):
            raise ValidationError("A senha deve conter caracteres especiais (ex: @#%!).")

        # 5. Sem espaços
        if ' ' in password:
            raise ValidationError("A senha não pode conter espaços.")

        # 6. Não repetir 3 caracteres consecutivos (ex: AAA, 111)
        if re.search(r'(.)\1\1', password):
            raise ValidationError("A senha não pode conter 3 caracteres iguais seguidos (ex: AAA).")

        # 7. Sem sequências óbvias de números ou letras (ex: 123, ABC)
        sequencias = ['123', '234', '345', '456', '567', '678', '789', '890',
                      'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
                      'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
                      'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz']
        for seq in sequencias:
            if seq in password.lower():
                raise ValidationError(f"A senha não pode conter sequências óbvias (ex: {seq}).")

    def get_help_text(self):
        return "Sua senha deve ter 8+ caracteres, combinando maiúsculas, minúsculas, números e símbolos (@#%). Não use espaços, sequências (123, abc) ou repetições (AAA)."