
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <timing.h>
#include <shine_mp3.h>

#define DR_WAV_IMPLEMENTATION

#include <dr_wav.h>

#define DR_MP3_IMPLEMENTATION

#include <dr_mp3.h>

void error(char *s);


int16_t *wavRead_int16(char *filename, uint32_t *sampleRate, uint32_t *channels, uint64_t *totalSampleCount) {
    int16_t *buffer = drwav_open_file_and_read_pcm_frames_s16(filename, channels, sampleRate, totalSampleCount, NULL);
    if (buffer == NULL) {
        drmp3_config pConfig;
        buffer = drmp3_open_file_and_read_pcm_frames_s16(filename, &pConfig, totalSampleCount, NULL);
        if (buffer != NULL) {
            *channels = pConfig.channels;
            *sampleRate = pConfig.sampleRate;
            *totalSampleCount *= *channels;
        } else {
            printf("read file [%s] error.\n", filename);
        }
    } else {
        *totalSampleCount *= *channels;
    }
    return buffer;
}


/* Some global vars. */
char *infname, *outfname;
FILE *outfile;
int quiet = 0;
int stereo = STEREO;
int force_mono = 0;

/* Write out the MP3 file */
int write_mp3(long bytes, void *buffer, void *config) {
    return fwrite(buffer, sizeof(unsigned char), bytes, outfile) / sizeof(unsigned char);
}

/* Output error message and exit */
void error(char *s) {
    fprintf(stderr, "Error: %s\n", s);
    exit(1);
}

static void print_usage() {
    printf("Audio Processing\n");
    printf("mp3 encoder && decoder\n");
    printf("blog: http://cpuimage.cnblogs.com/\n");
    printf("Usage: tinymp3 [options] <infile> <outfile>\n\n");
    printf("Use \"-\" for standard input or output.\n\n");
    printf("Options:\n");
    printf(" -h            this help message\n");
    printf(" -b <bitrate>  set the bitrate [8-320], default 64 kbit\n");
    printf(" -m            force encoder to operate in mono\n");
    printf(" -c            set copyright flag, default off\n");
    printf(" -j            encode in joint stereo (stereo data only)\n");
    printf(" -d            encode in dual-channel (stereo data only)\n");
    printf(" -q            quiet mode\n");
}

/* Use these default settings, can be overridden */
static void set_defaults(shine_config_t *config) {
    shine_set_config_mpeg_defaults(&config->mpeg);
}

/* Parse command line arguments */
static int parse_command(int argc, char **argv, shine_config_t *config) {
    int i = 0;

    if (argc < 3) return 0;

    while (argv[++i][0] == '-' && argv[i][1] != '\000' && argv[i][1] != ' ')
        switch (argv[i][1]) {
            case 'b':
                config->mpeg.bitr = atoi(argv[++i]);
                break;

            case 'm':
                force_mono = 1;
                break;

            case 'j':
                stereo = JOINT_STEREO;
                break;

            case 'd':
                stereo = DUAL_CHANNEL;
                break;

            case 'c':
                config->mpeg.copyright = 1;
                break;

            case 'q':
                quiet = 1;
                break;

            case 'v':
                quiet = 0;
                break;

            case 'h':
            default :
                return 0;
        }

    if (argc - i != 2) return 0;
    infname = argv[i++];
    outfname = argv[i];
    return 1;
}

/* Print some info about what we're going to encode */
static void check_config(shine_config_t *config) {
    static char *version_names[4] = {"2.5", "reserved", "II", "I"};
    static char *mode_names[4] = {"stereo", "joint-stereo", "dual-channel", "mono"};
    static char *demp_names[4] = {"none", "50/15us", "", "CITT"};

    printf("MPEG-%s layer III, %s  Psychoacoustic Model: Shine\n",
           version_names[shine_check_config(config->wave.samplerate, config->mpeg.bitr)],
           mode_names[config->mpeg.mode]);
    printf("Bitrate: %d kbps  ", config->mpeg.bitr);
    printf("De-emphasis: %s   %s %s\n",
           demp_names[config->mpeg.emph],
           ((config->mpeg.original) ? "Original" : ""),
           ((config->mpeg.copyright) ? "(C)" : ""));
    printf("Encoding \"%s\" to \"%s\"\n", infname, outfname);
}

int mainmp3(int argc, wchar_t *wargv[]) {
    char **argv = new char *[argc];
    for (int i = 0; i < argc; i++)
    {
        int length = WideCharToMultiByte(CP_ACP, 0, wargv[i], -1, NULL, 0, NULL, NULL);
        argv[i] = new char[length];
        WideCharToMultiByte(CP_ACP, 0, wargv[i], -1, argv[i], length, NULL, NULL);
    }
    shine_config_t config;
    shine_t s;
    int written;
    unsigned char *data;
    /* Set the default MPEG encoding paramters - basically init the struct */
    set_defaults(&config);

    if (!parse_command(argc, argv, &config)) {
        print_usage();
        exit(1);
    }

    quiet = quiet || !strcmp(outfname, "-");

    if (!quiet) {
        printf("Audio Processing\n");
        printf("mp3 encoder && decoder\n");
        printf("blog:http://cpuimage.cnblogs.com/\n");
    }
    uint32_t sampleRate = 0;
    uint64_t totalSampleCount = 0;
    uint32_t channels = 0;
    int16_t *data_in = wavRead_int16(infname, &sampleRate, &channels, &totalSampleCount);
    if (data_in == NULL)
        return -1;
    double startTime = now();
    config.wave.samplerate = sampleRate;
    config.wave.channels = (decltype(config.wave.channels))channels;

    if (force_mono)
        config.wave.channels = (decltype(config.wave.channels))1;

    /* See if samplerate and bitrate are valid */
    if (shine_check_config(config.wave.samplerate, config.mpeg.bitr) < 0)
        error("Unsupported samplerate/bitrate configuration.");

    /* open the output file */
    if (!strcmp(outfname, "-"))
        outfile = stdout;
    else
        outfile = fopen(outfname, "wb");
    if (!outfile) {
        fprintf(stderr, "Could not create \"%s\".\n", outfname);
        exit(1);
    }

    /* Set to stereo mode if wave data is stereo, mono otherwise. */
    if (config.wave.channels > 1)
        config.mpeg.mode = (decltype(config.mpeg.mode))stereo;
    else
        config.mpeg.mode = MONO;

    /* Initiate encoder */
    s = shine_initialise(&config);

    // assert(s != NULL);
    /* Print some info about the file about to be created (optional) */
    if (!quiet) check_config(&config);

    int samples_per_pass = shine_samples_per_pass(s) * channels;

    /* All the magic happens here */
    size_t count = totalSampleCount / samples_per_pass;
    int16_t *buffer = data_in;
    for (int i = 0; i < count; i++) {
        data = shine_encode_buffer_interleaved(s, buffer, &written);
        if (write_mp3(written, data, &config) != written) {
            fprintf(stderr, "mp3 encoder && decoder: write error\n");
            return 1;
        }
        buffer += samples_per_pass;
    }
    size_t last = totalSampleCount % samples_per_pass;
    if (last != 0) {
        int16_t *cache = (int16_t *) calloc(samples_per_pass, sizeof(int16_t));
        if (cache != NULL) {
            memcpy(cache, buffer, last * sizeof(int16_t));
            data = shine_encode_buffer_interleaved(s, cache, &written);
            free(cache);
            if (write_mp3(written, data, &config) != written) {
                fprintf(stderr, "mp3 encoder && decoder: write error\n");
                return 1;
            }
        }
    }
    /* Flush and write remaining data. */
    data = shine_flush(s, &written);
    write_mp3(written, data, &config);
    /* Close encoder. */
    shine_close(s);
    /* Close the MP3 file */
    fclose(outfile);
    free(data_in);
    double time_interval = calcElapsed(startTime, now());
    if (!quiet)
        printf("time interval: %d ms\n ", (int) (time_interval * 1000));

    return 0;
}
