import pygame

from settings import MAX_CARDS_IN_HAND, MAX_CARDS_IN_HAND_FOR_REFILL_EASY, HEIGHT
from button import button_objects

class InputHandler:
    def __init__(self, game):
        self.game = game

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if getattr(self.game, 'show_scoring_list', False):
                    if event.button == 4:
                        self.game.ui_manager.scroll_y = min(0, self.game.ui_manager.scroll_y + 35)
                    elif event.button == 5:
                        all_scores = self.game.score_manager.get_all_scores()
                        max_scroll = -max(0, len(all_scores) * 35 - (HEIGHT - 200))
                        self.game.ui_manager.scroll_y = max(max_scroll, self.game.ui_manager.scroll_y - 35)
                    elif event.button == 1:
                        self.check_menu_buttons(button_objects, event)

                else:
                    self.mouse_events(event)

            elif event.type == pygame.KEYDOWN and getattr(self.game, 'show_scoring_list', False):
                if event.key == pygame.K_ESCAPE:
                    self.game.show_scoring_list = False

    def mouse_events(self, event):
        if event.button == 1:
            button_clicked = self.check_menu_buttons(button_objects, event)
            if not button_clicked and not (self.game.new_game or self.game.sub_menu):
                self.carry_out_cards_logic(event)

    def check_menu_buttons(self, button_objects, event):
        for button in button_objects:
            if button.visible and button.check_event(event):
                return True
        return False

    def carry_out_cards_logic(self, event):
        mouse_pos = event.pos
        card_clicked = self.check_selection(mouse_pos)

        if len(self.game.cards_in_hand) == 0 and self.game.get_remaining_cards() == 0 and len(self.game.player_2_cards_in_hand) == 0:
            print('no cards left\n\n ---GAME WON!!!--- \n\n')
            return

        if not card_clicked:
            is_deck_clicked = any(card.rect.collidepoint(mouse_pos) for card in self.game.deck_cards)
            if is_deck_clicked:
                if ((len(self.game.cards_in_hand) < MAX_CARDS_IN_HAND and self.game.get_remaining_cards() == 0) or
                        len(self.game.cards_in_hand) <= MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
                    self.card_drawing(self.game.cards_in_hand, mouse_pos)
                else:
                    print('not enough cards laid out yet...')

            elif self.game.selected_card:
                for pile in self.game.piles.get_all_piles():
                    for card in pile:
                        self.game.stapels_logic(card, pile, mouse_pos)

    def card_drawing(self, cards_in_hand,  mouse_pos,
                     max_cards_hand=MAX_CARDS_IN_HAND, max_cards_hand_easy=MAX_CARDS_IN_HAND_FOR_REFILL_EASY):
        deck_clicked = any(card.rect.collidepoint(mouse_pos) for card in self.game.deck_cards)
        if not deck_clicked or len(self.game.empty_hand_slot)==0:
            return

        for card in self.game.deck_cards:
            card_col_n_empty_hand_slot = card.rect.collidepoint(mouse_pos) and (len(self.game.empty_hand_slot) > 0)
            if len(cards_in_hand) < max_cards_hand and self.game.get_remaining_cards() == 0:
                print('no cards left to draw from the Deck pile... \nnext players turn...')
                self._finish_turn()

            elif len(cards_in_hand) <= max_cards_hand_easy:
                self._refill_player_hand()
                self._finish_turn()

    def _finish_turn(self):
        if self.game.with_pc:
            self.game.current_turn = 'pc'
            self.game.pc_timer = pygame.time.get_ticks()
        else:
            # logic for drawing online
            pass

    def _refill_player_hand(self):
        print('draw cards...')
        for x in range(len(self.game.empty_hand_slot)):
            if self.game.get_remaining_cards() == 0:
                break
            pos_x = self.game.empty_hand_slot[x]
            self.game.card_generator(
                self.game.cards_in_hand,
                pos_x,
                self.game.deck.draw_card(),
                600,
            )

        self.game.hand_cards.add(self.game.cards_in_hand)
        self.game.all_cards.add(self.game.cards_in_hand)
        self.game.empty_hand_slot.clear()

    def check_selection(self, mouse_pos):
        card_clicked = False
        for card in self.game.hand_cards:
            if card.rect.collidepoint(mouse_pos):
                if self.game.selected_card:
                    self.game.selected_card.deselect()

                self.game.selected_card = card
                self.game.selected_card_value = card.value
                self.game.selected_card.select()

                print(f'card {card.value} from hand selected...')
                card_clicked = True
                break
        return card_clicked