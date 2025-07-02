
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