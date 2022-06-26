import pygame

def convert(coord, X, Y, size, scale):
    letter_to_coord = {
        "A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7
    }
    return (letter_to_coord[coord[0]] * size + (X-Y)/2 + 0.5*(1-scale)*size\
        ,(8 - int(coord[1])) * size + 0.5*(1-scale)*size)


def show(screen, piece, size, coordinate, X, Y):
    piece = piece
    scale = 0.9
    piece = pygame.transform.scale(piece, (size*scale, size*scale))
    screen.blit(piece, ((coordinate[1]) * size + 0.5*(1-scale)*size + (X-Y)/2\
        , coordinate[0] * size + 0.5*(1-scale)*size))

png = {
    "k": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_king.png'),
    "q": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_queen.png'),
    "p": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_pawn.png'),
    "n": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_knight.png'),
    "r": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_rook.png'),
    "b": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\black_bishop.png'),
    "K": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_king.png'),
    "Q": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_queen.png'),
    "P": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_pawn.png'),
    "N": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_knight.png'),
    "R": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_rook.png'),
    "B": pygame.image.load(r'C:\Users\Jonathanandzili\Personal CS Projects\chess\pieces\white_bishop.png')
}