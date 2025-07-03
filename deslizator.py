"""
Practice for the Programming Paradigms course based on a Tetris-style game using the wxPYTHON library.

This practice uses wx.Panel to represent the board.

Colors are assigned based on the letter:
a or A or unidentified character: dark green, b or B: blue, c or C: red.

The classes Board, Row, and Block from the previous practice have been reused (with some small modifications and comment revisions),
and parts of the interior practice code have been modified to be integrated into this MyFrame class.

To make moves, you need to drag blocks to the desired side or click on an empty position to drop the row above.
"""

import wx
from game_logic import Board

class MyFrame(wx.Frame):

    # Initialize the graphical user interface
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 550))
        self.SetTitle("Deslizator")
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 1, wx.ALL | wx.EXPAND, 5)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(left_sizer, 1, wx.ALL | wx.EXPAND, 5)

        file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(file_sizer, 0, 0, 0)

        self.start_button = wx.Button(self, wx.ID_ANY, "New Game")
        left_sizer.Add(self.start_button, 0, wx.ALL | wx.EXPAND, 5)

        speed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(speed_sizer, 0, 0, 0)

        speed_label = wx.StaticText(self, wx.ID_ANY, "Animation speed: ")
        speed_sizer.Add(speed_label, 0, wx.ALL, 5)

        self.speed_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "50", min=1, max=100)
        speed_sizer.Add(self.speed_ctrl, 0, 0, 0)

        rows_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(rows_sizer, 0, 0, 0)

        rows_label = wx.StaticText(self, wx.ID_ANY, "Number of rows: ")
        rows_sizer.Add(rows_label, 0, wx.ALL, 5)

        self.rows_ctrl = wx.SpinCtrl(self, wx.ID_ANY, "12", min=2, max=23)
        rows_sizer.Add(self.rows_ctrl, 0, 0, 0)

        moves_label = wx.StaticText(self, wx.ID_ANY, "Moves list:")
        left_sizer.Add(moves_label, 0, 0, 0)

        self.moves_listbox = wx.ListBox(self, wx.ID_ANY, choices=[], style=wx.LB_MULTIPLE)
        left_sizer.Add(self.moves_listbox, 1, wx.EXPAND, 0)

        self.score_label = wx.StaticText(self, wx.ID_ANY, "Score: 0")
        self.score_label.SetForegroundColour(wx.Colour(255, 0, 0))
        self.score_label.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Arial"))
        left_sizer.Add(self.score_label, 0, 0, 0)

        right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(right_sizer, 3, wx.ALL | wx.EXPAND, 5)

        self.letters_panel = wx.Panel(self)  
        self.letters_sizer = wx.BoxSizer(wx.VERTICAL)
        self.letters_panel.SetSizer(self.letters_sizer)
        bg_color = self.GetBackgroundColour()  # Get the frame's background color
        self.letters_panel.SetBackgroundColour(bg_color)
        right_sizer.Add(self.letters_panel, 0, wx.ALL | wx.EXPAND, 5)

        self.num_rows = self.rows_ctrl.GetValue()
        self.can_start = False

        self.panels_matrix = []

        self.draw_letters()

        self.board_and_numbers_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.board_and_numbers_sizer, 3, wx.ALL | wx.EXPAND, 5)
        self.graphic_panel = wx.Panel(self)
        self.graphic_board = wx.GridBagSizer(2, 0)
        self.graphic_panel.SetSizer(self.graphic_board)

        self.board_and_numbers_sizer.Add(self.graphic_panel, 10, wx.EXPAND | wx.ALL, 1)
        self.add_columns = True  # Prevent adding/removing growable columns again when changing number of rows
        self.fill_graphic_board()
        self.add_columns = False

        numbers_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.board_and_numbers_sizer.Add(numbers_sizer, 0, wx.LEFT | wx.EXPAND, 20)
        for num in range(10):
            number_label = wx.StaticText(self, wx.ID_ANY, str(num))
            number_label.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
            numbers_sizer.Add(number_label, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        self.status_label = wx.StaticText(self, wx.ID_ANY, "Load a file and set number of rows to start")
        self.status_label.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Arial"))
        main_sizer.Add(self.status_label, 0, 0, 0)

        self.read_file()

        self.SetSizer(main_sizer)

        self.Layout()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.draw_next_state, self.timer)
        self.Bind(wx.EVT_BUTTON, self.on_click_start_game, self.start_button)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_rows, self.rows_ctrl)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rows, self.rows_ctrl)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_speed, self.speed_ctrl)
        self.Bind(wx.EVT_TEXT, self.on_spin_speed, self.speed_ctrl)
        self.graphic_panel.Bind(wx.EVT_LEFT_DOWN, self.on_click_panel)
        self.graphic_panel.Bind(wx.EVT_LEFT_UP, self.off_click)
        self.waiting_for_move = False
        self.making_move = False
        self.time_to_draw_next_state = 1800 // self.num_rows  # More rows = faster, fewer rows = slower

    def on_spin_speed(self, event):
        self.time_variation = 50 / self.speed_ctrl.Value
        self.time_to_draw_next_state = int((1800 // self.num_rows) * self.time_variation)
        return None

    def read_file(self):
        filename = "list_rows_to_fall.txt"
        try:
            f = open(filename, "r")
            lines_list = []
            line_count = 0
            for line in f.readlines():
                lines_list.append(line)
                line_count += 1
            f.close()
            self.line_count = line_count
            self.lines_list = lines_list
            self.line_to_read = 0
            self.status_label.SetLabel("You can start the game.")
            self.can_start = True
        except:
            self.status_label.SetLabel("Error: make sure the file f.txt is in the same folder as the game.")
        return None

    # Starts the game by resetting the score to 0 and putting the first block row at the top...
    def on_click_start_game(self, event):
        self.start_game()

    def start_game(self):
        if self.can_start:
            self.score_label.SetLabel("Score: 0")
            self.moves_listbox.Clear()
            self.clear_graphic_board()
            self.status_label.SetLabel("Game started, waiting for move.")
            self.board = Board(self.num_rows, self.lines_list, self.line_to_read, self.line_count)
            self.board.read_line()
            self.draw_board()
            self.waiting_for_move = True
        else:
            self.status_label.SetLabel("Cannot start, file has not been read.")
        return None

    # Animates the moves happening on the board
    def draw_move(self):
        self.making_move = True
        if self.time_to_draw_next_state > 1000:
            self.time_to_draw_next_state = 1000
        self.need_to_draw_block_fall = False
        self.timer.Start(self.time_to_draw_next_state)

    # Moves the pieces down and checks each iteration if a row can be cleared
    def draw_next_state(self, event):
        self.fall_finished = False
        while self.row_to_fall != -1:  # If row is -1, all have fallen
            if self.row_to_fall != self.num_rows - 1 and self.board.rows[self.row_to_fall].blocks != []:
                # No point trying to make the last or an empty row fall
                while self.board.rows[self.row_to_fall + 1].blocks == []:
                    self.board.free_fall(self.row_to_fall)
                    self.draw_board()
                    self.row_to_fall += 1
                    if self.row_to_fall == self.num_rows - 1:
                        self.fall_finished = True
                        break
                    return None
                if not self.fall_finished:
                    self.board.block_fall(self.row_to_fall)
                    # If the next row has blocks, check if any block can fall
                    self.need_to_draw_block_fall = True
                    # Do not draw yet; wait to see if upper rows can fall
            self.row_to_fall -= 1
        if self.need_to_draw_block_fall:
            self.draw_board()
            self.need_to_draw_block_fall = False
            return None
        rows_cleared, last_cleared_row = self.board.try_clear_rows()
        if rows_cleared:
            if last_cleared_row == -1:
                self.status_label.SetLabel("You cleared a row with all blocks of the same color!!")
            elif last_cleared_row == self.num_rows - 1:
                last_cleared_row = self.num_rows - 2
            self.row_to_fall = last_cleared_row
            self.score_label.SetLabel("Score: " + str(self.board.score))
            self.draw_board()
            return None
        else:
            self.board.read_line()
            self.draw_board()
        if self.board.game_over:
            self.status_label.SetLabel("Game over!!!!!!!!!!!")
            self.waiting_for_move = False
        self.timer.Stop()
        self.making_move = False
        return None

    def draw_letters(self):
        self.letters_sizer.Clear(True)  # Clear previous letters

        for row in range(self.num_rows):
            letter = wx.StaticText(self.letters_panel, wx.ID_ANY, chr(ord("A") + row))  
            letter.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
            self.letters_sizer.Add(letter, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.letters_sizer.Layout()  # Refresh layout 
        return None

    def draw_board(self):
        self.clear_graphic_board()
        for row in range(self.num_rows):
            for block in self.board.rows[row].blocks:
                self.draw_block(block, row)
        self.Layout()
        return None
    
    def draw_block(self, block, row):
        if block.symbol == "#":
            for col in range(2 * block.start, (2 * (block.start+ block.length)) -1 ):
                self.panels_matrix[row][col].SetBackgroundColour((0,100,0))
                self.panels_matrix[row][col].Refresh()
        elif block.symbol == "$":
            for col in range(2 * block.start, (2 * (block.start+ block.length)) -1 ):
                self.panels_matrix[row][col].SetBackgroundColour(wx.Colour("blue"))
                self.panels_matrix[row][col].Refresh()
        else:
            for col in range(2 * block.start, (2 * (block.start+ block.length)) -1 ):
                self.panels_matrix[row][col].SetBackgroundColour(wx.Colour("red"))
                self.panels_matrix[row][col].Refresh()
        return None
    
    def get_color_from_letter(self, letter):
        if letter in ("a", "A"):
            return wx.Colour(0, 100, 0)  # Dark green
        elif letter in ("b", "B"):
            return wx.Colour(0, 0, 255)  # Blue
        elif letter in ("c", "C"):
            return wx.Colour(255, 0, 0)  # Red
        else:
            return wx.Colour(0, 100, 0)  # Default dark green

    def clear_graphic_board(self):
        for row in range(self.num_rows):
            for col in range (19):
                self.panels_matrix[row][col].SetBackgroundColour("white")
                self.panels_matrix[row][col].Refresh()
        return None
    
    def remove_graphic_board(self):
        for row in range(self.num_rows):
            self.graphic_board.RemoveGrowableRow(row)  
        self.graphic_board.Clear(True)
        return None

    def forward_event_to_graphic_panel(self, event):
        # Re-target the event to the graphic_panel
        new_event = wx.MouseEvent(event)
        new_event.SetEventObject(self.graphic_panel)
        wx.PostEvent(self.graphic_panel, new_event)
        
    def fill_graphic_board(self): 

        #self.status_label.SetLabel("Modifying rows.")
        # Reset the panels matrix
        self.panels_matrix = []
        for row in range(self.num_rows):
            self.panels_matrix.append([])
            for col in range(19):          
                block_panel = wx.Panel(self.graphic_panel, wx.ID_ANY)
                block_panel.SetBackgroundColour(wx.Colour("white"))
                self.graphic_board.Add(block_panel, (row, col),(0, 0), wx.EXPAND, 0)
                # Bind event to each child panel, forwarding to parent
                block_panel.Bind(wx.EVT_LEFT_DOWN, self.forward_event_to_graphic_panel)
                block_panel.Bind(wx.EVT_LEFT_UP, self.forward_event_to_graphic_panel)

                self.panels_matrix[row].append(block_panel)
                
        self.ID_panel0 = self.panels_matrix[0][0].GetId()

        for row in range(self.num_rows):
            self.graphic_board.AddGrowableRow(row)

        if self.add_columns:
            for col in range(19):
                if col % 2 == 0: 
                    self.graphic_board.AddGrowableCol(col)
        return None

    def on_click_panel(self, event):
        if self.waiting_for_move == True:
            if self.making_move == False:
                self.X = event.GetX()
                clicked_panel_pos = abs(event.GetId() - self.ID_panel0)
                self.clicked_row_index, self.clicked_column_index = self.get_position_of_the_move(clicked_panel_pos)
                if self.panels_matrix[self.clicked_row_index][self.clicked_column_index].GetBackgroundColour() == (255, 255, 255, 255):
                    self.status_label.SetLabel("Mouse pressed. Release it outside the board to cancel the empty move.")
                    self.letter = "-"
                    self.num_char = "-"
                else:
                    self.status_label.SetLabel("Release without moving or off the board to cancel the movement.")
                    self.letter = chr(65 + self.clicked_row_index)
                    self.num_char = str(self.clicked_column_index//2)
            else:
                self.status_label.SetLabel("Wait for the move to finish before making another one.")
        else:
            try:
                if self.board.game_over == True:
                    self.status_label.SetLabel("Start another game, this one is already over!!!")
            except:
                self.status_label.SetLabel("There is no game started.")
        return None
    
    def off_click(self, event):
        if self.waiting_for_move == True:
            if self.making_move == False:
                if self.num_char == "-":
                    direction = "-"
                else:
                    released_panel_position = abs(event.GetId() - self.ID_panel0)
                    _, column_index = self.get_position_of_the_move(released_panel_position)
                    # If the mouse leaves the panel and enters another one,
                    # the direction of movement is determined by the relative position 
                    # (left or right) of the other panel.
                    if column_index != self.clicked_column_index:
                        if column_index > self.clicked_column_index:
                            direction = ">"
                        else:
                            direction = "<"
                    else:
                        # Depend on the final mouse position in the same panel
                        # the direction of movement is choosen
                        if event.GetX() > self.X:
                            direction = ">"

                        elif event.GetX() < self.X:
                            direction = "<"
                        else:
                            direction =""
                play = self.letter + self.num_char + direction
                self.perform_mouse_move(play)
        return None
    
    def get_position_of_the_move(self, clicked_panel_position):
        row_index = clicked_panel_position // 19
        column_index = clicked_panel_position % 19
        return row_index, column_index
    
    def perform_mouse_move(self, move):
        if self.waiting_for_move:
            if self.board.game_over == False:
                if self.board.validate_move_and_execute(move) == 0:
                    self.moves_listbox.Insert(move, 0)
                    if move != "---":
                        self.row_to_fall = ord(move[0]) - 65
                    else:
                        self.row_to_fall = 0
                    self.draw_board()
                    self.draw_move()  
                else:
                    self.status_label.SetLabel(self.board.validate_move_and_execute(move))
            else:
                self.status_label.SetLabel("The game is over")
        else:
            self.status_label.SetLabel("No game started, please start one.")
        return None
    
    def on_spin_rows(self, event):
        self.waiting_for_move = False
        self.Freeze()
        self.remove_graphic_board()
        self.num_rows = self.rows_ctrl.GetValue()
        self.draw_letters()
        self.fill_graphic_board()
        self.waiting_for_move = False
        self.Layout()
        self.time_to_draw_next_state= 1800 // self.num_rows
        self.start_game()
        self.Thaw()
        return None
    
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()