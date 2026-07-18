#!/bin/bash
cd /opt/astro
./venv/bin/python -c 'from engine.corpus import get_corpus; print(get_corpus("gemma_extractions").describe())'
