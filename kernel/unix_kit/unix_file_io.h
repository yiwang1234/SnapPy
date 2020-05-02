/*
 *  unix_file_io.h
 *
 *  These three functions allow unix-style programs
 *  to read and save Triangulations.
 */

#include "SnapPea.h"

#include "kernel_namespace.h"

SNAPPEA_NAMESPACE_SCOPE_OPEN

extern Triangulation    *read_triangulation(const char *file_name);
extern Triangulation    *read_triangulation_from_string(const char *file_data);
extern Boolean          write_triangulation(Triangulation *manifold, const char *file_name);
extern char             *string_triangulation(Triangulation *manifold);

SNAPPEA_NAMESPACE_SCOPE_CLOSE
