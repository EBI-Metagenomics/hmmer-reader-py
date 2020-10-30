#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#ifndef MIN
#define MIN(X, Y) ((X) < (Y) ? (X) : (Y))
#endif

#define ERR_FILE 1
#define ERR_PARSER 2

enum token
{
    UNK = 0,
    NAME = 1,
    ACC = 2,
    LENG = 3,
    ALPH = 4,
    END = 5,
};

static enum token const TOKEN_ENUMS[] = {NAME, ACC, LENG, ALPH, END};
static char const*      TOKEN_STRINGS[] = {"NAME", "ACC", "LENG", "ALPH", "//"};
static unsigned const   TOKEN_SIZES[] = {4, 3, 4, 4, 2};

struct string
{
    char*  data;
    size_t size;
};

static inline bool string_equal(struct string* str, char const* data, size_t size)
{
    return strncmp(str->data, data, MIN(str->size, size)) == 0;
}

struct HMMFile
{
    FILE*          file;
    FILE* restrict estream;
    struct string  token;
    size_t         line_num;
    char           line[256 * 1024];
};

static inline void hmmfile_error(struct HMMFile const* hmmfile, char const* msg)
{
    fprintf(hmmfile->estream, "%s\n", msg);
}

static inline void hmmfile_parser_error(struct HMMFile const* hmmfile)
{
    fprintf(hmmfile->estream, "could not parse line %zu\n", hmmfile->line_num);
}

static inline int hmmfile_next_line(struct HMMFile* hmmfile)
{
    hmmfile->token.data = hmmfile->line;
    hmmfile->token.size = 0;
    ++hmmfile->line_num;
    return fgets(hmmfile->line, sizeof(hmmfile->line), hmmfile->file) != NULL;
}

static int hmmfile_next_token(struct HMMFile* hmmfile, bool skip_space)
{

    while (*hmmfile->token.data == ' ' && *hmmfile->token.data != '\n')
        ++hmmfile->token.data;

    char const* stop = hmmfile->token.data;

    while ((skip_space || *stop != ' ') && *stop != '\n')
        ++stop;

    hmmfile->token.size = stop - hmmfile->token.data;
    return hmmfile->token.size == 0;
}

static inline struct HMMFile hmmfile_open(char const* restrict path, FILE* restrict estream)
{
    struct HMMFile hmmfile;
    hmmfile.file = fopen(path, "r");
    hmmfile.estream = estream;
    hmmfile.token.data = NULL;
    hmmfile.token.size = 0;
    hmmfile.line_num = 0;
    return hmmfile;
}

static void hmmfile_close(struct HMMFile* hmmfile) { fclose(hmmfile->file); }

static int hmmfile_check_eof(struct HMMFile* hmmfile)
{
    if (!feof(hmmfile->file)) {
        if (ferror(hmmfile->file)) {
            fprintf(hmmfile->estream, "file error (%s)\n", strerror(errno));
            return ERR_FILE;
        } else {
            hmmfile_error(hmmfile, "stream ended prematurely");
            return ERR_FILE;
        }
    }
    return 0;
}

static enum token hmmfile_token(struct HMMFile* hmmfile)
{
    for (unsigned i = 0; i < 5; ++i) {

        if (string_equal(&hmmfile->token, TOKEN_STRINGS[i], TOKEN_SIZES[i])) {
            return TOKEN_ENUMS[i];
        }
    }

    return UNK;
}

#define META_BUFSIZE_NAME 1024
#define META_BUFSIZE_ACC 16
#define META_BUFSIZE_LENG 8
#define META_BUFSIZE_ALPH 8
#define META_BUFSIZE                                                                          \
    (META_BUFSIZE_NAME + META_BUFSIZE_ACC + META_BUFSIZE_LENG + META_BUFSIZE_ALPH)

struct meta
{
    struct string name;
    struct string acc;
    struct string leng;
    struct string alph;
    char          buffer[META_BUFSIZE];
};

static inline void meta_print_header(struct meta const* meta, FILE* restrict ostream)
{
    fprintf(ostream, "NAME\tACC\tLENG\tALPH\n");
}

static void meta_init(struct meta* meta)
{
    meta->name.data = meta->buffer;
    meta->name.size = 0;

    meta->acc.data = meta->name.data + META_BUFSIZE_NAME;
    meta->acc.size = 0;

    meta->leng.data = meta->acc.data + META_BUFSIZE_ACC;
    meta->leng.size = 0;

    meta->alph.data = meta->leng.data + META_BUFSIZE_LENG;
    meta->alph.size = 0;
}

static void meta_reset(struct meta* meta)
{
    meta->name.size = 0;
    meta->acc.size = 0;
    meta->leng.size = 0;
    meta->alph.size = 0;
}

static void meta_set(struct meta* meta, enum token token, struct string token_string)
{
    /* TODO check overflow */
    if (token == NAME) {
        memcpy(meta->name.data, token_string.data, token_string.size);
        meta->name.size = token_string.size;
    } else if (token == ACC) {
        memcpy(meta->acc.data, token_string.data, token_string.size);
        meta->acc.size = token_string.size;
    } else if (token == LENG) {
        memcpy(meta->leng.data, token_string.data, token_string.size);
        meta->leng.size = token_string.size;
    } else if (token == ALPH) {
        memcpy(meta->alph.data, token_string.data, token_string.size);
        meta->alph.size = token_string.size;
    }
}

static inline void meta_print(struct meta const* meta, FILE* restrict ostream)
{
    fprintf(ostream, "%.*s\t%.*s\t%.*s\t%.*s\n", (int)meta->name.size, meta->name.data,
            (int)meta->acc.size, meta->acc.data, (int)meta->leng.size, meta->leng.data,
            (int)meta->alph.size, meta->alph.data);
}

static inline bool meta_allset(struct meta const* meta)
{
    return (meta->name.size > 0 && meta->acc.size > 0 && meta->leng.size > 0 &&
            meta->alph.size > 0);
}

int meta_read(char const* filepath, FILE* restrict ostream, FILE* restrict estream)
{
    struct HMMFile hmmfile = hmmfile_open(filepath, estream);
    if (!hmmfile.file)
        return ERR_FILE;

    struct meta meta;
    meta_init(&meta);
    meta_print_header(&meta, ostream);

    enum token token = UNK;
    int        err = 0;

    while (hmmfile_next_line(&hmmfile)) {
        if (hmmfile_next_token(&hmmfile, false)) {
            hmmfile_parser_error(&hmmfile);
            goto err;
        }
        token = hmmfile_token(&hmmfile);
        if (token >= NAME && token <= ALPH) {
            hmmfile.token.data += hmmfile.token.size;
            if (hmmfile_next_token(&hmmfile, true)) {
                hmmfile_parser_error(&hmmfile);
                err = ERR_PARSER;
                goto err;
            }
            meta_set(&meta, token, hmmfile.token);
        } else if (token == END) {
            if (!meta_allset(&meta)) {
                hmmfile_error(&hmmfile, "some metadata is missing");
                err = ERR_PARSER;
                goto err;
            }
            meta_print(&meta, ostream);
            meta_reset(&meta);
        }
    }
    if (token != END) {
        hmmfile_error(&hmmfile, "ending token is missing");
        err = ERR_PARSER;
        goto err;
    }

    err = hmmfile_check_eof(&hmmfile);
    hmmfile_close(&hmmfile);
    return err;

err:
    hmmfile_close(&hmmfile);
    return err;
}
