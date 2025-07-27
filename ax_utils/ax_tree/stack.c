#include "Python.h"

#define MA 256
#define MI 64

typedef struct entry {
    PyObject * key;
    PyObject * value;
} entry_t;

typedef struct item_stack {
    unsigned int next;
    unsigned int max;
    unsigned int min;
    entry_t * entry_list;
} item_stack_t;

static item_stack_t *
item_stack_create(void)
{
    item_stack_t * stack = malloc(sizeof(item_stack_t));
    stack->entry_list = malloc(sizeof(entry_t)*MA);
    stack->max = MA;
    stack->min = 0;
    stack->next = 0;
    return stack;
}

static void
item_stack_free(item_stack_t * stack)
{
    free(stack->entry_list);
    free(stack);
}

static int
item_stack_push(item_stack_t *stack, PyObject *key, PyObject *value)
{
    entry_t * tmp;
    if(stack->next == stack->max)
    {
        stack->max += MA;
        stack->min += MI;
        tmp = realloc(stack->entry_list, sizeof(entry_t)*stack->max);
        if(tmp == NULL){return -1;}
        stack->entry_list = tmp;
    }

    stack->entry_list[stack->next].key = key;
    stack->entry_list[stack->next].value = value;
    stack->next++;
    return 0;
}

static entry_t *
item_stack_pop(item_stack_t *stack)
{
    entry_t * tmp;
    if(stack->next == stack->min)
    {
        stack->max -= MA;
        stack->min -= MI;
        tmp = realloc(stack->entry_list, sizeof(entry_t)*stack->max);
        if(tmp == NULL){return NULL;}
        stack->entry_list = tmp;
    }

    return &stack->entry_list[--stack->next];
}

static int
item_stack_iter(int *iter_pos, item_stack_t *stack, entry_t * result)
{
    if( *iter_pos == stack->next )
        return 0;

    result->key = stack->entry_list[*iter_pos].key;
    result->value = stack->entry_list[*iter_pos].value;
    (*iter_pos) = (*iter_pos) + 1;
    return 1;
}
