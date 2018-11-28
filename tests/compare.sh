#!/bin/bash
diff -a <(sort $1) <(sort $2)
