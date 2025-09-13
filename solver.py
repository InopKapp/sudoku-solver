
def issafe(mat,i,j,num,row,col,box):
    if (row[i] & (1<<num)) or (col[j] & (1<<num)) or (box[i//3*3+j//3] & (1<<num)):
        return False
    return True

def sudokusolve(mat,i,j,row,col,box):
    n = len(mat)
    if i == n-1 and j == n:
        return True
    if j == n:
        i += 1
        j = 0
    if mat[i][j] != 0:
        return sudokusolve(mat,i,j+1,row,col,box)
    for num in range(1,n+1):
        if issafe(mat,i,j,num,row,col,box):
            mat[i][j] = num
            row[i] |= (1<<num)
            col[j] |= (1<<num)
            box[i//3*3+j//3] |= (1<<num)
            if sudokusolve(mat,i,j+1,row,col,box):
                return True
            mat[i][j] = 0
            row[i] &= ~(1<<num)
            col[j] &= ~(1<<num)
            box[i//3*3+j//3] &= ~(1<<num)
    return False

def solve(mat):
    n = len(mat)
    row = [0]*n
    col = [0]*n
    box = [0]*n

    for i in range(n):
        for j in range(n):
            if mat[i][j] != 0:
                row[i] |= (1<<mat[i][j])        
                col[j] |= (1<<mat[i][j])        
                box[(i//3)*3+(j//3)] |= (1<<mat[i][j])        
    
    sudokusolve(mat,0,0,row,col,box)

if __name__ == "__main__":
    n = 9
    with open("sample_input.txt") as f:
        read_mat = f.readline()
        read_ans = f.readline()
    x = 0
    mat = [[0 for i in range(n)] for j in range(n)]
    ans = [[0 for i in range(n)] for j in range(n)]
    for i in range(n):
        for j in range(n):
            mat[i][j] = int(read_mat[x])
            ans[i][j] = int(read_ans[x])
            x += 1
    
    solve(mat)

    flag = 0
    for i in range(n):
        for j in range(n):
            if mat[i][j] != ans[i][j]:
                print("False")
                flag = 1
                break
        if flag == 1:
            break

    if flag==0:
        print("True")
    
    for i in range(n):
        for j in range(n):
            print(mat[i][j],end=" ")
        print()