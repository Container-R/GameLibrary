#include "sqlite3.h"
#include <stdio.h>
#include <string.h>

#define EXPECTED_ID "2025-07-30 19:33:53 4d8adfb30e03f9cf27f800a2c1ba3c48fb4ca1b08b0f5ed59a4d5ecbf45e20a3"
#define SCHEMA "CREATE TABLE save_item(id INTEGER PRIMARY KEY,qty INTEGER NOT NULL,pad BLOB NOT NULL)"
static int scalar_int(sqlite3 *db, const char *sql, int expected) {
    sqlite3_stmt *s = NULL; int ok = 0;
    if (sqlite3_prepare_v2(db,sql,-1,&s,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_step(s)!=SQLITE_ROW || sqlite3_column_type(s,0)!=SQLITE_INTEGER || sqlite3_column_int(s,0)!=expected) goto end;
    if (sqlite3_step(s)!=SQLITE_DONE) goto end;
    ok=1;
end:
    if (sqlite3_finalize(s)!=SQLITE_OK) ok=0;
    return ok;
}
static int scalar_text(sqlite3 *db, const char *sql, const char *expected) {
    sqlite3_stmt *s=NULL; int ok=0; const unsigned char *v;
    if (sqlite3_prepare_v2(db,sql,-1,&s,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_step(s)!=SQLITE_ROW || sqlite3_column_type(s,0)!=SQLITE_TEXT) goto end;
    v=sqlite3_column_text(s,0);
    if (!v || strcmp((const char *)v,expected)) goto end;
    if (sqlite3_step(s)!=SQLITE_DONE) goto end;
    ok=1;
end:
    if (sqlite3_finalize(s)!=SQLITE_OK) ok=0;
    return ok;
}
static int business(sqlite3 *db,int qty,int len) {
    return scalar_int(db,"SELECT count(*) FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'",1)
        && scalar_text(db,"SELECT sql FROM sqlite_schema WHERE type='table' AND name='save_item'",SCHEMA)
        && scalar_int(db,"SELECT count(*) FROM save_item",1)
        && scalar_int(db,"SELECT id FROM save_item",1)
        && scalar_int(db,"SELECT qty FROM save_item",qty)
        && scalar_int(db,"SELECT length(pad) FROM save_item",len)
        && scalar_int(db,"SELECT typeof(pad)='blob' AND pad=zeroblob(length(pad)) FROM save_item",1);
}
static int config(sqlite3 *db) {
    return scalar_int(db,"PRAGMA page_size",4096) && scalar_text(db,"PRAGMA journal_mode","delete");
}
static int create_db(const char *path, int source) {
    sqlite3 *db=NULL; int ok=0;
    if (sqlite3_open_v2(path,&db,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_exec(db,"PRAGMA page_size=4096; PRAGMA journal_mode=DELETE; " SCHEMA ";",NULL,NULL,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_exec(db,source?"INSERT INTO save_item VALUES(1,7,zeroblob(65536))":"INSERT INTO save_item VALUES(1,3,zeroblob(0))",NULL,NULL,NULL)!=SQLITE_OK) goto end;
    if (!config(db) || !business(db,source?7:3,source?65536:0)) goto end;
    ok=1;
end:
    if (db && sqlite3_close(db)!=SQLITE_OK) ok=0;
    return ok;
}
static int page_count(sqlite3 *db) {
    sqlite3_stmt *s=NULL; int n=-1;
    if (sqlite3_prepare_v2(db,"PRAGMA page_count",-1,&s,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_step(s)!=SQLITE_ROW || sqlite3_column_type(s,0)!=SQLITE_INTEGER) goto end;
    n=sqlite3_column_int(s,0);
    if (sqlite3_step(s)!=SQLITE_DONE) n=-1;
end:
    if (sqlite3_finalize(s)!=SQLITE_OK) n=-1;
    return n;
}
static int branch(int cancel) {
    const char *name=cancel?"cancel":"complete";
    const char *sp=cancel?"cancel/source.db":"complete/source.db";
    const char *dp=cancel?"cancel/dest.db":"complete/dest.db";
    sqlite3 *src=NULL,*dst=NULL,*read=NULL; sqlite3_backup *b=NULL;
    int ok=0,n,rc=-1,fin=-1,steps=0,remaining=-1,total=-1,done=0;
    if (!create_db(sp,1) || !create_db(dp,0)) goto end;
    if (sqlite3_open_v2(sp,&src,SQLITE_OPEN_READONLY,NULL)!=SQLITE_OK) goto end;
    if (sqlite3_open_v2(dp,&dst,SQLITE_OPEN_READWRITE,NULL)!=SQLITE_OK) goto end;
    /* Both creation connections were closed; verify persisted target before init. */
    if (!config(src)||!config(dst)||!business(src,7,65536)||!business(dst,3,0)) goto end;
    n=page_count(src); if(n<2 || n>128) goto end;
    printf("{\"branch\":\"%s\",\"event\":\"precheck\",\"page_size\":4096,\"journal_mode\":\"delete\",\"source_pages\":%d,\"source_row\":[1,7,65536],\"target_row\":[1,3,0],\"target_reopened\":true}\n",name,n);
    b=sqlite3_backup_init(dst,"main",src,"main"); if(!b) goto end;
    /* No destination connection API between successful init and finish. */
    do {
        rc=sqlite3_backup_step(b,1); steps++;
        remaining=sqlite3_backup_remaining(b); total=sqlite3_backup_pagecount(b);
        printf("{\"branch\":\"%s\",\"event\":\"step\",\"index\":%d,\"rc\":%d,\"remaining\":%d,\"pagecount\":%d}\n",name,steps,rc,remaining,total);
        if ((rc!=SQLITE_OK && rc!=SQLITE_DONE)||total!=n||remaining<0||remaining>n) goto end;
        if(rc==SQLITE_DONE) { done=1; if(remaining!=0) goto end; }
        if(cancel) { if(rc!=SQLITE_OK || remaining<=0) goto end; break; }
        if(rc==SQLITE_OK && remaining<=0) goto end;
    } while(!done && steps<128);
    if(!cancel && !done) goto end;
    fin=sqlite3_backup_finish(b); b=NULL;
    printf("{\"branch\":\"%s\",\"event\":\"finish\",\"rc\":%d,\"saw_done\":%s}\n",name,fin,done?"true":"false");
    if(fin!=SQLITE_OK) goto end;
    if(sqlite3_close(dst)!=SQLITE_OK) goto end; dst=NULL;
    if(sqlite3_close(src)!=SQLITE_OK) goto end; src=NULL;
    if(sqlite3_open_v2(dp,&read,SQLITE_OPEN_READONLY,NULL)!=SQLITE_OK) goto end;
    if(!config(read)||!business(read,cancel?3:7,cancel?0:65536)) goto end;
    if(sqlite3_close(read)!=SQLITE_OK) goto end; read=NULL;
    printf("{\"branch\":\"%s\",\"event\":\"readback\",\"row\":[1,%d,%d],\"schema_exact\":true,\"row_count\":1,\"zero_blob_exact\":true}\n",name,cancel?3:7,cancel?0:65536);
    ok=1;
end:
    /* On failure retain databases; exactly one finish per successful init. */
    if(b) { int cleanup=sqlite3_backup_finish(b); b=NULL; printf("{\"branch\":\"%s\",\"event\":\"cleanup_finish\",\"rc\":%d}\n",name,cleanup); }
    if(read && sqlite3_close(read)!=SQLITE_OK) ok=0;
    if(dst && sqlite3_close(dst)!=SQLITE_OK) ok=0;
    if(src && sqlite3_close(src)!=SQLITE_OK) ok=0;
    return ok;
}
int main(void) {
    if(sqlite3_libversion_number()!=3050004 || strcmp(sqlite3_sourceid(),EXPECTED_ID) || sqlite3_threadsafe()!=0) return 2;
    printf("{\"event\":\"identity\",\"version\":\"%s\",\"source_id\":\"%s\",\"threadsafe\":0}\n",sqlite3_libversion(),sqlite3_sourceid());
    if(!branch(0)) { puts("{\"event\":\"failure\",\"branch\":\"complete\"}"); return 3; }
    if(!branch(1)) { puts("{\"event\":\"failure\",\"branch\":\"cancel\"}"); return 4; }
    puts("{\"event\":\"all_checks_passed\"}");
    return 0;
}
