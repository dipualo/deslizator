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

class MyFrame(wx.Frame):

    # Initialize the graphical user interface
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((650, 450))
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

        self.letters_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.letters_sizer, 0, wx.BOTTOM | wx.TOP | wx.EXPAND, 10)

        self.num_rows = self.rows_ctrl.GetValue()
        self.can_start = False

        self.panels_matrix = []

        self.draw_letters()

        self.board_and_numbers_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.board_and_numbers_sizer, 3, wx.ALL | wx.EXPAND, 5)
        self.graphic_board = wx.GridBagSizer(2, 0)
        self.board_and_numbers_sizer.Add(self.graphic_board, 10, wx.EXPAND, 1)

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
        self.letters_sizer.Clear(True)
        for row in range(self.num_rows):
            letter = wx.StaticText(self, wx.ID_ANY, chr(ord("A") + row))
            letter.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
            self.letters_sizer.Add(letter, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
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
        self.graphic_board = wx.GridBagSizer(2, 0)
        return None

    def fill_graphic_board(self):        
        for row in range(self.num_rows):
            self.panels_matrix.append([])
            for col in range(19):                
                block_panel = wx.Panel(self, wx.ID_ANY)
                block_panel.Bind(wx.EVT_LEFT_DOWN, self.on_click_panel)
                block_panel.Bind(wx.EVT_LEFT_UP, self.off_click)
                block_panel.SetBackgroundColour(wx.Colour("white"))
                self.graphic_board.Add(block_panel, (row, col),(0, 0), wx.EXPAND, 0)
                block_panel.Refresh()
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
        self.start_game()
        self.remove_graphic_board()
        self.num_rows = self.rows_ctrl.GetValue()
        self.draw_letters()
        self.fill_graphic_board()
        self.waiting_for_move = False
        self.Layout()
        self.time_to_draw_next_state= 1800 // self.num_rows
        return None
    
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class Board():
    def __init__(self, num_rows, lines_list, line_to_read, total_lines):
        self.num_rows = num_rows
        self.lines_list = lines_list
        self.line_to_read = line_to_read
        self.total_lines = total_lines
        self.rows = []
        for _ in range(self.num_rows):
            self.rows.append(Row())
        self.game_over = False
        self.score = 0
        return None

    def read_line(self):
        if self.rows[0].blocks != []:
            self.game_over = True
            return None
        else:
            if self.total_lines - 1 == self.line_to_read:
                self.line_to_read = 0
            line = self.lines_list[self.line_to_read]
            if len(line) > 11:  # Just in case there are more than 10 characters in a line
                line = line[0:10]
                print("Make sure the file is correct!!! (More than 10 characters in a row)")
            if ord(line[len(line) - 1]) != 10:
                line += chr(10)  # Add newline character if missing
            self.line_to_read += 1
            self.place_read_line(line)
            return None

    # Adds the read line from the file to the board with its blocks
    def place_read_line(self, line):
        pos = 0
        while pos < (len(line) - 1):
            # We don't care about the newline character at the end: line[len(line) - 1]
            if line[pos] != " ":
                length = 0
                start_pos = pos
                if line[pos] in ("b", "B"):
                    char = line[pos]
                    while char == line[pos]:
                        if length == 0:
                            start_pos = start_pos  # initial position of the block
                        length += 1
                        if pos == len(line) - 1:
                            break
                        pos += 1
                    symbol = "$"  # blocks starting with b or B get symbol $
                elif line[pos] in ("c", "C"):
                    char = line[pos]
                    while char == line[pos]:
                        if length == 0:
                            start_pos = start_pos
                        length += 1
                        if pos == len(line) - 1:
                            break
                        pos += 1
                    symbol = "%"  # blocks starting with c or C get symbol %
                else:  # for a or A (or other), treated similarly
                    char = line[pos]
                    while char == line[pos]:
                        if length == 0:
                            start_pos = start_pos
                        length += 1
                        if pos == len(line) - 1:
                            break
                        pos += 1
                    symbol = "#"  # default symbol
                self.rows[0].add_block(start_pos, length, symbol)
            else:
                pos += 1
        return None

    # Validates the move syntax (--- or a capital letter A-L, a positive number < num_rows and a symbol < or >)
    # and if the move can be made
    def validate_move_and_execute(self, move):
        if len(move) == 3:
            if move == "---":
                return 0
            else:
                # Convert capital letter row to number
                row = ord(move[0]) - 65
                if row < 0 or row > self.num_rows - 1:
                    return "Syntax error in first position: must be a row."
                try:
                    cell_to_move = int(move[1])
                except:
                    return "Syntax error in second position: must be a number."
                cell = Block(cell_to_move, 1, "X")
                # Create a block of length 1 to check if there is a block at that position
                block_found = False
                pos = 0
                for block in self.rows[row].blocks:
                    if block.share_position_with(cell):
                        block_found = True
                        break
                    pos += 1
                if not block_found:
                    return "Error, no block in that cell."
                else:
                    if move[2] == "<":
                        if pos == 0:
                            if self.rows[row].blocks[pos].start == 0:
                                return "Error, block is at the left edge."
                            else:
                                # Move block to left edge
                                self.rows[row].blocks[pos].start = 0
                                return 0
                        else:
                            return self.move_block_left(row, pos)
                    elif move[2] == ">":
                        if len(self.rows[row].blocks) == pos + 1:
                            if self.rows[row].blocks[pos].start + self.rows[row].blocks[pos].length - 1 == 9:
                                return "Error, block is at the right edge."
                            else:
                                self.rows[row].blocks[pos].start = 10 - self.rows[row].blocks[pos].length
                                return 0
                        else:
                            return self.move_block_right(row, pos)
                    else:
                        return "No movement detected."
        else:
            return "You must move the mouse before releasing it to make moves."

    def move_block_left(self, row, pos):
        # Check that blocks are not adjacent on the left
        if ((self.rows[row].blocks[pos - 1].start + self.rows[row].blocks[pos - 1].length) -
            self.rows[row].blocks[pos].start) == 0:
            return "Error, block is stuck to another on the left."
        else:
            # Move block left until it touches the previous block
            self.rows[row].blocks[pos].start = (self.rows[row].blocks[pos - 1].start +
                                                self.rows[row].blocks[pos - 1].length)
            return 0

    def move_block_right(self, row, pos):
        # Same as above but for the right
        if (self.rows[row].blocks[pos + 1].start - (self.rows[row].blocks[pos].start +
            self.rows[row].blocks[pos].length)) == 0:
            return "Error, block is stuck to another on the right."
        else:
            self.rows[row].blocks[pos].start = (self.rows[row].blocks[pos + 1].start -
                                                self.rows[row].blocks[pos].length)
            return 0

    def fall(self, row):
        while self.rows[row + 1].blocks == []:
            # If the row below has no blocks, the blocks fall directly
            self.free_fall(row)
            row += 1
            if row == self.num_rows - 1:
                return None  # fall has finished at the last row
        self.block_fall(row)
        return None

    def free_fall(self, row):
        for block in self.rows[row].blocks:
            # Copy blocks from current row to the row below
            self.rows[row + 1].blocks.append(block)
        # Clear blocks from the current row
        self.rows[row].blocks = []
        return None

    def block_fall(self, row):
        block_pos = 0
        blocks_to_remove = []
        for block in self.rows[row].blocks:
            if self.can_fall(block, row):
                blocks_to_remove, new_pos = self.fall_block(row, block, block_pos, blocks_to_remove)
                next_row = row + 1
                if next_row != self.num_rows - 1:
                    while self.can_fall(block, next_row):
                        blocks_to_remove, new_pos = self.fall_block(next_row, block, new_pos, blocks_to_remove)
                        next_row += 1
                        if next_row == self.num_rows - 1:
                            break
            block_pos += 1
        self.remove_blocks(blocks_to_remove)
        return None

    def can_fall(self, block_above, row):
        can_fall = True
        for block_below in self.rows[row + 1].blocks:
            if block_above.share_position_with(block_below):
                can_fall = False
                break
        return can_fall

    def remove_blocks(self, blocks_to_remove):
        pos = 0
        removed_blocks_count = [0] * self.num_rows
        for number in blocks_to_remove:
            if pos % 2 == 0:
                row = number
            else:
                block_pos = number
                block_pos -= removed_blocks_count[row]
                self.rows[row].blocks.pop(block_pos)
                self.rows[row].blocks.sort()
                removed_blocks_count[row] += 1
            pos += 1
        return None

    def fall_block(self, row, block, block_pos, blocks_to_remove):
        self.rows[row + 1].blocks.append(block)
        blocks_to_remove.append(row)
        blocks_to_remove.append(block_pos)
        block_pos = self.rows[row + 1].sort_blocks()
        return blocks_to_remove, block_pos

    def count_points_on_board(self):
        points = 0
        for row in self.rows:
            for block in row.blocks:
                points += block.length
        return points

    def try_clear_rows(self):
        pos_row = 0
        for row in self.rows:
            if row.blocks != []:
                all_same_symbol = True
                symbol = row.blocks[0].symbol
                occupied_cells = ""
                for block in row.blocks:
                    if block.symbol != symbol and all_same_symbol:
                        all_same_symbol = False
                    occupied_cells += block.block_cells()
                if len(occupied_cells) == 10:
                    self.score += 10
                    self.rows[pos_row].blocks = []
                    if all_same_symbol:
                        self.score += self.count_points_on_board()
                        self.rows = []
                        for _ in range(self.num_rows):
                            self.rows.append(Row())
                        return True, -1
                    else:
                        return True, pos_row
            pos_row += 1
        return False, -1

class Row():

    def __init__(self):
        self.blocks = []

    def add_block(self, start, length, symbol):
        self.blocks.append(Block(start, length, symbol))
        return None

    def sort_blocks(self):
        pos_new = 0
        for block in self.blocks:
            if block.start > self.blocks[-1].start or pos_new == len(self.blocks) - 1:
                break
            pos_new += 1
        self.blocks.sort()
        return pos_new

class Block():

    def __init__(self, start, length, symbol):
        self.start = start
        self.length = length
        self.symbol = symbol
        return None

    def block_cells(self):
        cells = ""
        for i in range(self.length):
            cells += str(self.start + i)
        return cells

    def share_position_with(self, block_below):
        shared = False
        cells_above = self.block_cells()
        for i in range(block_below.length):
            if cells_above.find(str(block_below.start + i)) != -1:
                shared = True
                break
        return shared

    def __lt__(self, other):
        return self.start < other.start

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()