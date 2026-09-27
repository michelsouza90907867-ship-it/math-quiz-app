import random
import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex

# Configuração do tamanho da janela no computador para testes (Modo Mobile)
Window.size = (360, 640)

# ============================================================
# CORES
# ============================================================

BG = '#0B1120'
CARD = '#172033'
BLUE = '#2563EB'
CYAN = '#38BDF8'
GREEN = '#22C55E'
RED = '#F87171'
YELLOW = '#FACC15'
PURPLE = '#A78BFA'
WHITE = '#F8FAFC'
MUTED = '#94A3B8'
DARK_INPUT = '#0F172A'


# ============================================================
# WIDGETS REUTILIZÁVEIS
# ============================================================

class RoundedButton(Button):
    button_color = ListProperty([0, 0, 0, 1])

    def __init__(self, color=BLUE, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = get_color_from_hex(color)
        self.button_color = self.base_color

        with self.canvas.before:
            self.canvas_color = Color(*self.button_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_state(self, instance, value):
        if value == 'down':
            self.canvas_color.rgba = [c * 0.8 for c in self.base_color[:3]] + [self.base_color[3]]
        else:
            self.canvas_color.rgba = self.base_color


class Card(BoxLayout):
    def __init__(self, color=CARD, radius=22, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex(color))
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(radius)]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ============================================================
# TELA INICIAL (MENU)
# ============================================================

class MenuScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        self.record_label.text = f"RECORDE: {app.recorde}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(22), dp(25), dp(22), dp(20)],
            spacing=dp(14)
        )

        title = Label(
            text='MATH QUIZ',
            font_size='34sp',
            bold=True,
            color=get_color_from_hex(CYAN),
            size_hint_y=None,
            height=dp(60)
        )
        root.add_widget(title)

        subtitle = Label(
            text='Teste seus conhecimentos e desafie sua mente!',
            font_size='15sp',
            color=get_color_from_hex(MUTED),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(45)
        )
        subtitle.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(20), None)))
        root.add_widget(subtitle)

        self.record_label = Label(
            text='RECORDE: 0',
            font_size='17sp',
            bold=True,
            color=get_color_from_hex(YELLOW),
            size_hint_y=None,
            height=dp(38)
        )
        root.add_widget(self.record_label)

        info = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(190)
        )

        items = [
            ('NIVEIS', 'A dificuldade aumenta'),
            ('TEMPO', '60 segundos por rodada'),
            ('VIDAS', '3 chances'),
            ('RECORDES', 'Tente superar sua marca'),
        ]

        for title_text, body_text in items:
            card = Card(
                orientation='vertical',
                padding=dp(8),
                spacing=dp(2)
            )
            
            lbl_title = Label(
                text=title_text,
                font_size='14sp',
                bold=True,
                color=get_color_from_hex(CYAN),
                halign='center'
            )
            lbl_title.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))

            lbl_body = Label(
                text=body_text,
                font_size='11sp',
                color=get_color_from_hex(MUTED),
                halign='center',
                valign='middle'
            )
            lbl_body.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(8), None)))

            card.add_widget(lbl_title)
            card.add_widget(lbl_body)
            info.add_widget(card)

        root.add_widget(info)
        root.add_widget(BoxLayout())  # Espaçador dinâmico

        play = RoundedButton(
            text='JOGAR',
            font_size='22sp',
            bold=True,
            color=GREEN,
            size_hint_y=None,
            height=dp(64)
        )
        play.bind(on_release=self.start_game)
        root.add_widget(play)

        exit_button = RoundedButton(
            text='SAIR',
            font_size='15sp',
            color='#334155',
            size_hint_y=None,
            height=dp(48)
        )
        exit_button.bind(on_release=lambda *_: App.get_running_app().stop())
        root.add_widget(exit_button)

        footer = Label(
            text='Aprenda, responda e tente bater seu recorde.',
            font_size='13sp',
            color=get_color_from_hex(MUTED),
            size_hint_y=None,
            height=dp(35),
            halign='center'
        )
        footer.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        root.add_widget(footer)

        self.add_widget(root)

    def start_game(self, *_):
        game = self.manager.get_screen('game')
        game.start_game()
        self.manager.current = 'game'


# ============================================================
# TELA DO JOGO
# ============================================================

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pontos = 0
        self.vidas = 3
        self.sequencia = 0
        self.nivel = 1
        self.tempo = 60
        self.jogo_ativo = False
        self.num1 = 0
        self.num2 = 0
        self.operacao = '+'
        self.resposta_correta = 0

        # Carregamento seguro de sons no VS Code
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.sound_correct = self._load_sound(os.path.join(base_dir, 'correct.wav'))
        self.sound_wrong = self._load_sound(os.path.join(base_dir, 'wrong.wav'))
        self.sound_gameover = self._load_sound(os.path.join(base_dir, 'gameover.wav'))

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(18), dp(18), dp(18), dp(18)],
            spacing=dp(10)
        )

        header = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8)
        )

        back = RoundedButton(
            text='MENU',
            font_size='13sp',
            bold=True,
            color='#334155',
            size_hint_x=None,
            width=dp(82)
        )
        back.bind(on_release=self.go_menu)
        header.add_widget(back)

        self.logo = Label(
            text='MATH QUIZ',
            font_size='20sp',
            bold=True,
            color=get_color_from_hex(CYAN)
        )
        header.add_widget(self.logo)

        self.record_label = Label(
            text='RECORDE: 0',
            font_size='14sp',
            bold=True,
            color=get_color_from_hex(YELLOW),
            size_hint_x=None,
            width=dp(110)
        )
        header.add_widget(self.record_label)

        root.add_widget(header)

        status = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(62),
            spacing=dp(6)
        )

        self.points_label = Label(
            text='PONTOS\n0',
            font_size='15sp',
            bold=True,
            color=get_color_from_hex(WHITE)
        )
        self.lives_label = Label(
            text='VIDAS\n3',
            font_size='15sp',
            bold=True,
            color=get_color_from_hex(RED)
        )
        self.time_label = Label(
            text='TEMPO\n60s',
            font_size='15sp',
            bold=True,
            color=get_color_from_hex(PURPLE)
        )

        status.add_widget(self.points_label)
        status.add_widget(self.lives_label)
        status.add_widget(self.time_label)
        root.add_widget(status)

        self.card = Card(
            orientation='vertical',
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(12)
        )

        self.level_label = Label(
            text='NIVEL 1',
            font_size='15sp',
            bold=True,
            color=get_color_from_hex(CYAN),
            size_hint_y=None,
            height=dp(28)
        )
        self.card.add_widget(self.level_label)

        self.question_label = Label(
            text='0 + 0',
            font_size='42sp',
            bold=True,
            color=get_color_from_hex(WHITE)
        )
        self.card.add_widget(self.question_label)

        self.answer = TextInput(
            hint_text='Digite sua resposta',
            multiline=False,
            input_filter='int',
            font_size='23sp',
            halign='center',
            size_hint_y=None,
            height=dp(58),
            background_normal='',
            background_active='',
            background_color=get_color_from_hex(DARK_INPUT),
            foreground_color=get_color_from_hex(WHITE),
            hint_text_color=get_color_from_hex('#64748B'),
            padding=[dp(10), dp(12)]
        )
        self.answer.bind(on_text_validate=self.check_answer)
        self.card.add_widget(self.answer)

        self.check_button = RoundedButton(
            text='CONFERIR',
            font_size='18sp',
            bold=True,
            color=BLUE,
            size_hint_y=None,
            height=dp(56)
        )
        self.check_button.bind(on_release=self.check_answer)
        self.card.add_widget(self.check_button)

        root.add_widget(self.card)

        self.feedback = Label(
            text='Digite a resposta e toque em CONFERIR.',
            font_size='15sp',
            bold=True,
            color=get_color_from_hex(MUTED),
            size_hint_y=None,
            height=dp(52),
            halign='center'
        )
        self.feedback.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        root.add_widget(self.feedback)

        new_game = RoundedButton(
            text='NOVO JOGO',
            font_size='15sp',
            bold=True,
            color='#334155',
            size_hint_y=None,
            height=dp(48)
        )
        new_game.bind(on_release=self.start_game)
        root.add_widget(new_game)

        self.add_widget(root)

    def _load_sound(self, path):
        """Carrega o arquivo de som se ele existir no disco."""
        if os.path.exists(path):
            return SoundLoader.load(path)
        return None

    def play_sound(self, sound):
        if sound:
            sound.stop()
            sound.play()

    def start_game(self, *_):
        app = App.get_running_app()

        self.pontos = 0
        self.vidas = 3
        self.sequencia = 0
        self.nivel = 1
        self.tempo = 60
        self.jogo_ativo = True

        self.feedback.text = 'Boa sorte!'
        self.feedback.color = get_color_from_hex(MUTED)
        self.answer.text = ''
        self.check_button.text = 'CONFERIR'

        Clock.unschedule(self.tick)
        Clock.schedule_interval(self.tick, 1)

        self.record_label.text = f'RECORDE: {app.recorde}'
        self.new_question()
        self.update_ui()

        Clock.schedule_once(lambda dt: setattr(self.answer, 'focus', True), 0.1)

    def new_question(self):
        limit = min(10 + self.nivel * 5, 100)
        self.operacao = random.choice(['+', '-', '*', '/'])

        if self.operacao == '+':
            self.num1 = random.randint(1, limit)
            self.num2 = random.randint(1, limit)
            self.resposta_correta = self.num1 + self.num2

        elif self.operacao == '-':
            self.num1 = random.randint(10, limit)
            self.num2 = random.randint(1, self.num1)
            self.resposta_correta = self.num1 - self.num2

        elif self.operacao == '*':
            mult = min(5 + self.nivel, 15)
            self.num1 = random.randint(1, mult)
            self.num2 = random.randint(1, mult)
            self.resposta_correta = self.num1 * self.num2

        else:  # Divisão exata
            divisor_max = min(5 + self.nivel, 12)
            self.num2 = random.randint(1, divisor_max)
            self.resposta_correta = random.randint(1, divisor_max)
            self.num1 = self.resposta_correta * self.num2

        signal = 'x' if self.operacao == '*' else ('÷' if self.operacao == '/' else self.operacao)
        self.question_label.text = f'{self.num1} {signal} {self.num2}'
        self.level_label.text = f'NIVEL {self.nivel}'

    def check_answer(self, *_):
        if not self.jogo_ativo:
            return

        text = self.answer.text.strip()

        if not text:
            self.feedback.text = 'Digite uma resposta!'
            self.feedback.color = get_color_from_hex(YELLOW)
            return

        try:
            user_answer = int(text)
        except ValueError:
            return

        if user_answer == self.resposta_correta:
            self.play_sound(self.sound_correct)
            self.sequencia += 1
            gained = 10 + ((self.sequencia - 1) * 2)
            self.pontos += gained

            self.feedback.text = f'CORRETO! +{gained} pontos'
            self.feedback.color = get_color_from_hex('#4ADE80')

            if self.sequencia % 5 == 0:
                self.nivel += 1
                self.feedback.text = f'NIVEL {self.nivel}! A dificuldade aumentou.'

        else:
            self.play_sound(self.sound_wrong)
            self.vidas -= 1
            self.sequencia = 0
            self.pontos = max(0, self.pontos - 5)

            self.feedback.text = f'ERRADO! A resposta era {self.resposta_correta}.'
            self.feedback.color = get_color_from_hex(RED)

            if self.vidas <= 0:
                self.end_game()
                return

        app = App.get_running_app()
        if self.pontos > app.recorde:
            app.recorde = self.pontos
            app.save_record()

        self.answer.text = ''
        self.new_question()
        self.update_ui()
        self.answer.focus = True

    def tick(self, _dt):
        if not self.jogo_ativo:
            return

        self.tempo -= 1

        if self.tempo <= 10:
            self.time_label.color = get_color_from_hex(RED)
        else:
            self.time_label.color = get_color_from_hex(PURPLE)

        self.update_ui()

        if self.tempo <= 0:
            self.end_game()

    def end_game(self):
        self.jogo_ativo = False
        Clock.unschedule(self.tick)
        self.play_sound(self.sound_gameover)

        app = App.get_running_app()

        if self.pontos > app.recorde:
            app.recorde = self.pontos
            app.save_record()

        self.feedback.text = f'FIM DE JOGO! Pontuacao: {self.pontos}'
        self.feedback.color = get_color_from_hex(YELLOW)
        self.check_button.text = 'JOGO ENCERRADO'
        self.record_label.text = f'RECORDE: {app.recorde}'
        self.update_ui()

    def update_ui(self):
        app = App.get_running_app()

        self.points_label.text = f'PONTOS\n{self.pontos}'
        self.lives_label.text = f'VIDAS\n{self.vidas}'
        self.time_label.text = f'TEMPO\n{self.tempo}s'
        self.record_label.text = f'RECORDE: {app.recorde}'

    def go_menu(self, *_):
        self.jogo_ativo = False
        Clock.unschedule(self.tick)
        self.manager.current = 'menu'


# ============================================================
# APLICATIVO
# ============================================================

class MathQuizApp(App):

    def build(self):
        self.title = 'Math Quiz'
        self.recorde = self.load_record()

        Window.clearcolor = get_color_from_hex(BG)

        manager = ScreenManager()
        manager.add_widget(MenuScreen(name='menu'))
        manager.add_widget(GameScreen(name='game'))

        return manager

    def record_path(self):
        return os.path.join(self.user_data_dir, 'recorde.json')

    def load_record(self):
        try:
            with open(self.record_path(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                return int(data.get('recorde', 0))
        except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
            return 0

    def save_record(self):
        try:
            os.makedirs(self.user_data_dir, exist_ok=True)
            with open(self.record_path(), 'w', encoding='utf-8') as f:
                json.dump({'recorde': self.recorde}, f)
        except OSError:
            pass

    def on_stop(self):
        self.save_record()


if __name__ == '__main__':
    MathQuizApp().run()