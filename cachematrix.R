## Programming Assignment 2: Lexical Scoping
##
## Matrix inversion is a costly computation. These two functions work together
## to avoid repeating it: makeCacheMatrix() wraps a matrix in a closure that can
## remember ("cache") its inverse, and cacheSolve() uses that cache so solve()
## only runs when the inverse is not already known.
##
## Example:
##   m <- makeCacheMatrix(matrix(c(2, 0, 0, 2), 2, 2))
##   cacheSolve(m)   # computes the inverse with solve()
##   cacheSolve(m)   # prints "getting cached data" and returns the cache
##   m$set(matrix(c(1, 2, 3, 4), 2, 2))   # new matrix => cache is cleared
##   cacheSolve(m)   # computes the inverse again


## makeCacheMatrix: creates a special "matrix" object, which is really a list
## of four functions that share one environment:
##   set(y)           stores a new matrix and clears the cached inverse
##   get()            returns the matrix
##   setinverse(inv)  stores the inverse in the cache
##   getinverse()     returns the cached inverse (NULL if not computed yet)
## 'x' and 'inv' live in the enclosing environment of these functions, and the
## <<- operator is used to modify them from inside set() and setinverse().

makeCacheMatrix <- function(x = matrix()) {
        inv <- NULL
        set <- function(y) {
                x <<- y
                inv <<- NULL            # the matrix changed: invalidate cache
        }
        get <- function() x
        setinverse <- function(inverse) inv <<- inverse
        getinverse <- function() inv
        list(set = set, get = get,
             setinverse = setinverse,
             getinverse = getinverse)
}


## cacheSolve: returns the inverse of the special "matrix" created by
## makeCacheMatrix(). If the inverse is already cached (and the matrix has not
## changed since), it is returned from the cache with a message; otherwise the
## inverse is computed with solve(), stored in the cache and returned.
## Extra arguments in '...' are passed on to solve(). The matrix is assumed to
## be square and invertible.

cacheSolve <- function(x, ...) {
        ## Return a matrix that is the inverse of 'x'
        inv <- x$getinverse()
        if (!is.null(inv)) {
                message("getting cached data")
                return(inv)
        }
        data <- x$get()
        inv <- solve(data, ...)
        x$setinverse(inv)
        inv
}
